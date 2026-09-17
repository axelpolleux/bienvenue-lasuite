"""Pulls a Grist table and upserts it into Postgres by grist_row_id.

Non-destructive: rows deleted in Grist are left as-is in Postgres rather
than cascade-deleted, so existing agent_todo_statuses never dangle.
"""

import logging

from src.onboarding.models import (
    Colleague,
    Document,
    Template,
    ValidationTypeChoices,
    Training,
    TodoItem,
)
from src.onboarding.services.grist_client import client

logger = logging.getLogger(__name__)

SYNCABLE_TABLES = ["Templates", "TodoItems", "Colleagues", "Documents", "Trainings"]


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


def sync_todo_items(records):
    synced, skipped = 0, 0
    for record in records:
        fields = record["fields"]
        template = _template_for(fields)
        if template is None:
            skipped += 1
            continue
        validation_type = fields.get("ValidationType") or ValidationTypeChoices.MANUAL
        if validation_type not in ValidationTypeChoices.values:
            validation_type = ValidationTypeChoices.MANUAL
        TodoItem.objects.update_or_create(
            grist_row_id=str(record["id"]),
            defaults={
                "template": template,
                "label": fields.get("Label") or "",
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


_SYNC_FUNCTIONS = {
    "Templates": sync_templates,
    "TodoItems": sync_todo_items,
    "Colleagues": sync_colleagues,
    "Documents": sync_documents,
    "Trainings": sync_trainings,
}


def sync_table(table_name):
    """Pull one Grist table and upsert it. Returns the number of rows synced."""
    sync_fn = _SYNC_FUNCTIONS.get(table_name)
    if sync_fn is None:
        raise ValueError(f"Unknown Grist table: {table_name}")
    records = client.list_records(table_name)
    return sync_fn(records)


def sync_all():
    """Sync every table, Templates first so children can resolve their parent."""
    return {table: sync_table(table) for table in SYNCABLE_TABLES}
