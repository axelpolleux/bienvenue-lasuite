"""One-off utility: snapshot the team's cloud Grist doc into our self-hosted one.

Run this whenever the cloud doc (edited by the team) is considered "final" for
a given moment, to keep a local, offline copy — e.g. as a demo fallback if
the internet or the cloud account is unavailable.

This replaces the self-hosted doc's content wholesale (wipe + recreate), it
does not merge. Grist row ids are re-assigned on the destination doc, so the
Template ref on child rows is remapped accordingly.
"""

from django.core.management.base import BaseCommand

from src.onboarding.services.grist_client import GristClient, client as cloud_client

# Our local self-hosted instance (see docker-compose.yml's "grist" service).
# Not a real secret: throwaway local-only doc, same key used throughout dev.
SELF_HOSTED_BASE_URL = "http://grist:8484"
SELF_HOSTED_API_KEY = "8e7d6a30c6cd3ec05e8afa34875c735af5fa795f"
SELF_HOSTED_DOC_ID = "2ukGv1AtPNK3vmfWRSBLGw"

CHILD_TABLES = ["TodoItems", "Colleagues", "Documents", "Trainings"]

# The cloud doc and our self-hosted doc were built independently and don't
# use identical column casing on every field — rename on the way in.
FIELD_RENAMES = {
    "Documents": {"URL": "Url"},
    "Trainings": {"VideoURL": "VideoUrl"},
}


def _rename_fields(table, fields):
    renames = FIELD_RENAMES.get(table, {})
    return {renames.get(key, key): value for key, value in fields.items()}


class Command(BaseCommand):
    help = "Copies every table's records from the configured (cloud) Grist doc into our self-hosted doc."

    def handle(self, *args, **options):
        dest = GristClient(
            base_url=SELF_HOSTED_BASE_URL,
            api_key=SELF_HOSTED_API_KEY,
            doc_id=SELF_HOSTED_DOC_ID,
        )

        self.stdout.write("Wiping self-hosted tables...")
        for table in ["Templates", *CHILD_TABLES]:
            existing = dest.list_records(table)
            if existing:
                dest.delete_records(table, [r["id"] for r in existing])

        self.stdout.write("Copying Templates...")
        source_templates = cloud_client.list_records("Templates")
        template_id_map = {}
        if source_templates:
            created = dest.create_records(
                "Templates", [row["fields"] for row in source_templates]
            )
            for source_row, dest_row in zip(source_templates, created):
                template_id_map[source_row["id"]] = dest_row["id"]
        self.stdout.write(f"  Templates: {len(source_templates)} copied")

        for table in CHILD_TABLES:
            source_rows = cloud_client.list_records(table)
            remapped, skipped = [], 0
            for row in source_rows:
                fields = dict(row["fields"])
                new_template_id = template_id_map.get(fields.get("Template"))
                if new_template_id is None:
                    skipped += 1
                    continue
                fields["Template"] = new_template_id
                remapped.append(_rename_fields(table, fields))
            if remapped:
                dest.create_records(table, remapped)
            suffix = f", {skipped} skipped (no matching template)" if skipped else ""
            self.stdout.write(f"  {table}: {len(remapped)} copied{suffix}")

        self.stdout.write(
            self.style.SUCCESS(
                "Mirror complete — self-hosted Grist now matches the cloud doc."
            )
        )
