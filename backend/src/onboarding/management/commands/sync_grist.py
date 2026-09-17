"""Management command to pull every Grist table and upsert it into Postgres."""

from django.core.management.base import BaseCommand

from src.onboarding.services.grist_sync import sync_all


class Command(BaseCommand):
    help = "Pulls all 5 Grist tables and upserts Templates/TodoItems/etc. by grist_row_id."

    def handle(self, *args, **options):
        self.stdout.write("Syncing from Grist...")
        results = sync_all()
        for table, count in results.items():
            self.stdout.write(f"  {table}: {count} row(s) synced")
        self.stdout.write(self.style.SUCCESS("Grist sync complete."))
