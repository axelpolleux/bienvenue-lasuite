"""Pulls a Grist table and upserts it into Postgres by grist_row_id.

Non-destructive: rows deleted in Grist are left as-is in Postgres rather
than cascade-deleted, so existing agent_todo_statuses never dangle.
"""

from datetime import datetime, timezone as dt_timezone
import logging

from django.db import transaction

from src.onboarding.models import (
    Agent,
    AgentTodoStatus,
    Colleague,
    Document,
    RoleChoices,
    Template,
    ValidationTypeChoices,
    Training,
    TodoItem,
)
from src.onboarding.services.grist_client import client

logger = logging.getLogger(__name__)

# Templates first (children resolve their parent through it), Members right
# after (it also references Templates, nothing depends on Members).
SYNCABLE_TABLES = [
    "Templates",
    "Members",
    "TodoItems",
    "Colleagues",
    "Documents",
    "Trainings",
    "MemberChecklist",
]


def _template_for(fields):
    """Resolve the parent Template from a child row's `Template` ref field."""
    ref = fields.get("Template")
    if not ref:
        return None
    return Template.objects.filter(grist_row_id=str(ref)).first()


def sync_templates(records):
    synced = 0
    for record in records:
        fields = record["fields"]
        Template.objects.update_or_create(
            grist_row_id=str(record["id"]),
            defaults={
                "name": fields.get("Name") or "",
                "email_signature": fields.get("EmailSignature") or "",
            },
        )
        synced += 1
    return synced


def sync_members(records):
    """Provision/update new agents from the RH-maintained Members list.

    Only ever sets `role` on first creation — never downgrades an existing
    agent's role (e.g. a manager mistakenly added to this table).
    """
    synced, skipped = 0, 0
    for record in records:
        fields = record["fields"]
        email = (fields.get("Email") or "").strip().lower()
        if not email:
            skipped += 1
            continue
        template = _template_for(fields)
        name = fields.get("Name") or email.split("@")[0].replace(".", " ").title()

        agent, created = Agent.objects.get_or_create(
            email=email,
            defaults={
                "name": name,
                "role": RoleChoices.NEW_AGENT,
                "assigned_template": template,
            },
        )
        if not created:
            agent.name = name
            agent.assigned_template = template
            agent.save(update_fields=["name", "assigned_template"])
        synced += 1
    if skipped:
        logger.warning("grist_sync: skipped %d Members with no email", skipped)
    return synced


def sync_todo_items(records):
    synced, skipped = 0, 0
    for record in records:
        fields = record["fields"]
        template = _template_for(fields)
        if template is None:
            skipped += 1
            continue
        kind = (fields.get("Kind") or "").upper()
        label = fields.get("Label") or ""
        if kind == "AUTO":
            validation_type = (
                ValidationTypeChoices.SIGNATURE
                if "signature" in label.lower()
                else ValidationTypeChoices.API_CHECK
            )
        elif kind == "MANUEL":
            validation_type = ValidationTypeChoices.MANUAL
        else:
            validation_type = fields.get("ValidationType") or ValidationTypeChoices.MANUAL

        if validation_type not in ValidationTypeChoices.values:
            validation_type = ValidationTypeChoices.MANUAL

        TodoItem.objects.update_or_create(
            grist_row_id=str(record["id"]),
            defaults={
                "template": template,
                "label": label,
                "description": fields.get("Description") or "",
                "service_link": fields.get("ServiceLink") or None,
                "doc_url": fields.get("DocUrl") or None,
                "order": fields.get("Order") or 0,
                "validation_type": validation_type,
            },
        )
        synced += 1
    if skipped:
        logger.warning("grist_sync: skipped %d TodoItems with no matching Template", skipped)
    return synced


def sync_colleagues(records):
    synced, skipped = 0, 0
    for record in records:
        fields = record["fields"]
        template = _template_for(fields)
        if template is None:
            skipped += 1
            continue
        Colleague.objects.update_or_create(
            grist_row_id=str(record["id"]),
            defaults={
                "template": template,
                "name": fields.get("Name") or "",
                "tchap_link": fields.get("TchapLink") or "",
            },
        )
        synced += 1
    if skipped:
        logger.warning("grist_sync: skipped %d Colleagues with no matching Template", skipped)
    return synced


def sync_documents(records):
    synced, skipped = 0, 0
    for record in records:
        fields = record["fields"]
        template = _template_for(fields)
        if template is None:
            skipped += 1
            continue
        Document.objects.update_or_create(
            grist_row_id=str(record["id"]),
            defaults={
                "template": template,
                "title": fields.get("Title") or "",
                # Column is "URL" on the cloud doc, "Url" on our self-hosted one.
                "url": fields.get("URL") or fields.get("Url") or "",
                "format": fields.get("Format") or "pdf",
            },
        )
        synced += 1
    if skipped:
        logger.warning("grist_sync: skipped %d Documents with no matching Template", skipped)
    return synced


def sync_trainings(records):
    synced, skipped = 0, 0
    for record in records:
        fields = record["fields"]
        template = _template_for(fields)
        if template is None:
            skipped += 1
            continue
        Training.objects.update_or_create(
            grist_row_id=str(record["id"]),
            defaults={
                "template": template,
                "title": fields.get("Title") or "",
                # Column is "VideoURL" on the cloud doc, "VideoUrl" on our self-hosted one.
                "video_url": fields.get("VideoURL") or fields.get("VideoUrl") or "",
                "duration_minutes": fields.get("DurationMinutes") or None,
            },
        )
        synced += 1
    if skipped:
        logger.warning("grist_sync: skipped %d Trainings with no matching Template", skipped)
    return synced


def _parse_grist_timestamp(val):
    """Parse Grist timestamp (seconds since epoch) into timezone-aware datetime."""
    if not val:
        return None
    try:
        return datetime.fromtimestamp(float(val), tz=dt_timezone.utc)
    except (ValueError, TypeError, OverflowError):
        return None


def sync_member_checklist(records):
    """Sync custom manager-created tasks and member progress from MemberChecklist."""
    grist_members = client.list_records_safe("Members")
    member_by_id = {
        rec["id"]: (rec["fields"].get("Email") or "").strip().lower()
        for rec in grist_members
        if (rec.get("fields", {}).get("Email") or "").strip()
    }
    agent_by_email = {
        a.email.strip().lower(): a
        for a in Agent.objects.select_related("assigned_template").all()
    }

    synced = 0
    for record in records:
        fields = record.get("fields", {})
        member_row_id = fields.get("Member")
        email = member_by_id.get(member_row_id)
        agent = agent_by_email.get(email) if email else None
        if not agent or not agent.assigned_template:
            continue

        custom_label = (fields.get("CustomLabel") or "").strip()
        item_ref = fields.get("Item")
        done = bool(fields.get("Done"))
        done_at = _parse_grist_timestamp(fields.get("DoneAt"))

        if not item_ref and custom_label:
            todo, _ = TodoItem.objects.update_or_create(
                grist_row_id=f"mc-{record['id']}",
                defaults={
                    "agent": agent,
                    "template": agent.assigned_template,
                    "label": custom_label,
                    "description": (fields.get("CustomDescription") or "").strip(),
                    "order": 100 + int(record["id"]),
                    "validation_type": ValidationTypeChoices.MANUAL,
                },
            )
            status_obj, _ = AgentTodoStatus.objects.get_or_create(
                agent=agent,
                todo_item=todo,
            )
            status_obj.done = done
            status_obj.done_at = done_at if done else None
            status_obj.save(update_fields=["done", "done_at"])
            synced += 1
        elif item_ref:
            todo = TodoItem.objects.filter(grist_row_id=str(item_ref)).first()
            if todo:
                status_obj, created = AgentTodoStatus.objects.get_or_create(
                    agent=agent,
                    todo_item=todo,
                    defaults={"done": done, "done_at": done_at},
                )
                if not created and status_obj.done != done:
                    status_obj.done = done
                    status_obj.done_at = done_at if done else None
                    status_obj.save(update_fields=["done", "done_at"])
                synced += 1

    return synced


_SYNC_FUNCTIONS = {
    "Templates": sync_templates,
    "Members": sync_members,
    "TodoItems": sync_todo_items,
    "Colleagues": sync_colleagues,
    "Documents": sync_documents,
    "Trainings": sync_trainings,
    "MemberChecklist": sync_member_checklist,
}


def sync_table(table_name):
    """Pull one Grist table and upsert it. Returns the number of rows synced."""
    sync_fn = _SYNC_FUNCTIONS.get(table_name)
    if sync_fn is None:
        raise ValueError(f"Unknown Grist table: {table_name}")
    if table_name == "TodoItems":
        records = client.list_records_safe("ChecklistItems") or client.list_records_safe("TodoItems")
    else:
        records = client.list_records_safe(table_name)
    return sync_fn(records)


def sync_all():
    """Sync every table, Templates first so children can resolve their parent."""
    with transaction.atomic():
        return {table: sync_table(table) for table in SYNCABLE_TABLES}


def _build_member_email_map(records):
    """Build a mapping from normalized lowercased email to Grist member row id."""
    return {
        (rec["fields"].get("Email") or "").strip().lower(): rec["id"]
        for rec in records
        if (rec.get("fields", {}).get("Email") or "").strip()
    }


def _compute_checklist_deltas(agents, member_by_email, checklist_lookup, checklist_id_lookup=None):
    """Compute MemberChecklist rows to update and create for all active agents."""
    to_update, to_create = [], []
    affected_members = set()
    checklist_id_lookup = checklist_id_lookup or {}

    for agent in agents:
        member_id = member_by_email.get(agent.email.strip().lower())
        if not member_id or not agent.assigned_template:
            continue

        status_map = {s.todo_item_id: s for s in agent.todo_statuses.all()}

        for item in agent.get_all_todos():
            if not item.grist_row_id:
                continue

            status = status_map.get(item.id)
            done = bool(status and status.done)
            done_at_str = (
                status.done_at.date().isoformat()
                if status and status.done and status.done_at
                else None
            )

            if item.grist_row_id.startswith("mc-"):
                try:
                    mc_id = int(item.grist_row_id.replace("mc-", ""))
                except (ValueError, TypeError):
                    continue
                existing = checklist_id_lookup.get(mc_id)
                if existing:
                    existing_fields = existing.get("fields", {})
                    existing_done = bool(existing_fields.get("Done"))
                    existing_done_at = existing_fields.get("DoneAt")
                    if existing_done != done or (done and existing_done_at != done_at_str):
                        to_update.append({
                            "id": mc_id,
                            "fields": {"Done": done, "DoneAt": done_at_str},
                        })
                        affected_members.add(member_id)
                continue

            try:
                item_id = int(item.grist_row_id)
            except (ValueError, TypeError):
                continue

            key = (member_id, item_id)
            existing = checklist_lookup.get(key)

            if existing:
                existing_fields = existing.get("fields", {})
                existing_done = bool(existing_fields.get("Done"))
                existing_done_at = existing_fields.get("DoneAt")
                if existing_done != done or (done and existing_done_at != done_at_str):
                    to_update.append({
                        "id": existing["id"],
                        "fields": {"Done": done, "DoneAt": done_at_str},
                    })
                    affected_members.add(member_id)
            else:
                to_create.append({
                    "Member": member_id,
                    "Item": item_id,
                    "Done": done,
                    "DoneAt": done_at_str,
                })
                affected_members.add(member_id)

    return to_update, to_create, affected_members


def push_progress_to_grist():
    """Push agent checklist progress to Grist MemberChecklist table."""
    grist_members = client.list_records_safe("Members")
    member_by_email = _build_member_email_map(grist_members)
    if not member_by_email:
        return {"updated": 0, "created": 0, "members_affected": 0}

    existing_rows = client.list_records_safe("MemberChecklist")
    checklist_lookup = {
        (rec["fields"].get("Member"), rec["fields"].get("Item")): rec
        for rec in existing_rows
        if "fields" in rec
    }
    checklist_id_lookup = {
        rec["id"]: rec for rec in existing_rows if "id" in rec
    }
    new_agents = (
        Agent.objects.filter(role=RoleChoices.NEW_AGENT)
        .select_related("assigned_template")
        .prefetch_related(
            "assigned_template__todo_items",
            "custom_todo_items",
            "todo_statuses",
        )
    )
    to_update, to_create, affected = _compute_checklist_deltas(
        new_agents, member_by_email, checklist_lookup, checklist_id_lookup
    )
    if to_update:
        client.update_records("MemberChecklist", to_update)
    if to_create:
        client.create_records("MemberChecklist", to_create)

    return {
        "updated": len(to_update),
        "created": len(to_create),
        "members_affected": len(affected),
    }
