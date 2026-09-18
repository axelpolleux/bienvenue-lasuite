"""Management command to translate all Grist content to English."""

from django.core.management.base import BaseCommand
from src.onboarding.services.grist_client import client
from src.onboarding.services.grist_sync import sync_all


def safe_update_records(table, records):
    for rec in records:
        client.update_records(table, [rec])


class Command(BaseCommand):
    help = "Translates Templates, ChecklistItems, Comments, Services, and Member roles in Grist to English."

    def handle(self, *args, **options):
        self.stdout.write("Translating Grist records to English...")

        # 1. Templates
        templates_updates = [
            {
                "id": 1,
                "fields": {
                    "Name": "Digital Suite Onboarding",
                    "Description": (
                        "The reference onboarding pathway: complete discovery of "
                        "La Suite Numérique tools. Serves as foundation for service templates "
                        "and default fallback."
                    ),
                },
            },
            {
                "id": 2,
                "fields": {
                    "Name": "Digital & IT Pathway",
                    "Description": "For technical and digital positions: includes code repository access.",
                    "MatchKeywords": "digital, IT, technical, developer, system, data",
                },
            },
            {
                "id": 3,
                "fields": {
                    "Name": "HR Pathway",
                    "Description": "For HR roles: includes access to internal HR management tools.",
                    "MatchKeywords": "HR, human resources, recruitment, payroll, training",
                },
            },
            {
                "id": 4,
                "fields": {
                    "Name": "Communications Pathway",
                    "Description": "For communications positions: includes brand guidelines and document templates.",
                    "MatchKeywords": "communication, community, press, editorial",
                },
            },
        ]
        safe_update_records("Templates", templates_updates)
        self.stdout.write(self.style.SUCCESS("Updated Templates."))

        # 2. Comments
        comments_updates = [
            {
                "id": 1,
                "fields": {
                    "Text": "Technical onboarding lead for the team — contact her first for Fichiers issues."
                },
            },
            {
                "id": 2,
                "fields": {
                    "Text": "Quick onboarding with Fichiers on day one. Follow-up meeting scheduled for Friday."
                },
            },
            {
                "id": 3,
                "fields": {
                    "Text": "Visio call and charter steps pending — follow up gently, currently busy with interviews."
                },
            },
            {
                "id": 4,
                "fields": {
                    "Text": "Internal transfer scheduled for late December. Hand over recruitment files to Elise before departure."
                },
            },
            {
                "id": 5,
                "fields": {
                    "Text": "Smooth onboarding, fully autonomous by the second week."
                },
            },
        ]
        safe_update_records("Comments", comments_updates)
        self.stdout.write(self.style.SUCCESS("Updated Comments."))

        # 3. Services
        services_updates = [
            {"id": 1, "fields": {"Name": "Digital Department"}},
            {"id": 2, "fields": {"Name": "Human Resources"}},
            {"id": 3, "fields": {"Name": "Communications Department"}},
        ]
        safe_update_records("Services", services_updates)
        self.stdout.write(self.style.SUCCESS("Updated Services."))

        # 4. Members roles
        members_updates = [
            {"id": 1, "fields": {"Role": "IT & Support Lead"}},
            {"id": 2, "fields": {"Role": "Digital Project Officer"}},
            {"id": 3, "fields": {"Role": "Executive Assistant"}},
            {"id": 4, "fields": {"Role": "Talent Acquisition Specialist"}},
            {"id": 5, "fields": {"Role": "HR Operations Manager"}},
            {"id": 6, "fields": {"Role": "Head of Communications"}},
            {"id": 7, "fields": {"Role": "Communications Specialist"}},
        ]
        safe_update_records("Members", members_updates)
        self.stdout.write(self.style.SUCCESS("Updated Member roles."))

        # 5. ChecklistItems
        checklist_label_map = {
            "rejoindre tchap": ("Join Tchap and the team channel", "Sovereign instant messaging for the civil service."),
            "messagerie": ("Configure professional email", "First-time login and mailbox settings."),
            "visioconférence": ("Test a video call on Visio", "Create and join a test meeting."),
            "docs": ("Explore collaborative editing on Docs", "Create a document and invite a colleague."),
            "charte": ("Read the IT and security charter", "Official guideline document available on Fichiers."),
            "signature": ("Confirm official email signature", "Generate and confirm standard email signature."),
            "fichiers": ("Activate and verify Fichiers storage", "Automated verification once your account is provisioned."),
            "gestion rh": ("Access internal HR management tool", "Verify access rights and organization mapping in HR tool."),
            "charte graphique": ("Discover brand guidelines and templates", "Brand assets and document templates available on Fichiers."),
            "ec": ("Activate and verify Fichiers storage", "Automated verification once your account is provisioned."),
            "test": ("Welcome check-in", "Introductory onboarding check-in."),
        }

        checklist_records = client.list_records_safe("ChecklistItems")
        checklist_updates = []
        for rec in checklist_records:
            fields = rec.get("fields", {})
            label = (fields.get("Label") or "").lower()
            if not label:
                continue

            for key, (new_label, new_desc) in checklist_label_map.items():
                if key in label:
                    checklist_updates.append({
                        "id": rec["id"],
                        "fields": {
                            "Label": new_label,
                            "Description": new_desc,
                        },
                    })
                    break

        if checklist_updates:
            safe_update_records("ChecklistItems", checklist_updates)
            self.stdout.write(self.style.SUCCESS(f"Updated {len(checklist_updates)} ChecklistItems."))

        # 6. Run sync_all
        self.stdout.write("Synchronizing updated Grist records to PostgreSQL...")
        results = sync_all()
        self.stdout.write(self.style.SUCCESS(f"Sync complete: {results}"))
