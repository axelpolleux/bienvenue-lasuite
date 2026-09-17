"""Management command to seed demo template, users, and tasks."""

from django.core.management.base import BaseCommand
from django.db import transaction
from src.onboarding.models import (
    Template,
    Agent,
    TodoItem,
    Colleague,
    Document,
    Training,
    AgentTodoStatus,
    RoleChoices,
    ValidationTypeChoices,
    DocumentFormatChoices,
)


class Command(BaseCommand):
    """Seeds initial demonstration data for local development."""

    help = "Seeds initial templates, demo agents, tasks, and resources."

    @transaction.atomic
    def handle(self, *args, **options):
        """Execute deterministic seed operations."""
        self.stdout.write("Seeding demo data...")

        # 1. Master Template
        template, _ = Template.objects.update_or_create(
            grist_row_id="demo-template-core",
            defaults={
                "name": "Common Core Administration",
                "email_signature": (
                    "Alex Martin\n"
                    "Chargé de mission — Direction Interministérielle du Numérique\n"
                    "alex.martin@gouv.fr | +33 1 00 00 00 00\n"
                    "https://lasuite.numerique.gouv.fr"
                ),
            },
        )

        # 2. Todo Items
        todo_fichiers, _ = TodoItem.objects.update_or_create(
            grist_row_id="demo-todo-fichiers",
            defaults={
                "template": template,
                "order": 1,
                "label": "Activate and verify my file storage space",
                "description": "Fichiers is your personal and shared file storage space.",
                "service_link": "https://fichiers.numerique.gouv.fr",
                "doc_url": "https://docs.numerique.gouv.fr/docs/0b8b54fb-ef03-48fa-99b8-b88a289ceb8c/",
                "validation_type": ValidationTypeChoices.API_CHECK,
            },
        )

        todo_tchap, _ = TodoItem.objects.update_or_create(
            grist_row_id="demo-todo-tchap",
            defaults={
                "template": template,
                "order": 2,
                "label": "Set up my instant messaging app",
                "description": "Tchap is the secure instant messaging app used across the public administration.",
                "service_link": "https://tchap.gouv.fr",
                "doc_url": "https://docs.numerique.gouv.fr/docs/1aec951f-c8d8-49c0-ab9e-9a1aac629b3e/",
                "validation_type": ValidationTypeChoices.MANUAL,
            },
        )

        todo_signature, _ = TodoItem.objects.update_or_create(
            grist_row_id="demo-todo-signature",
            defaults={
                "template": template,
                "order": 3,
                "label": "Set up my official email signature template",
                "description": "Configure and validate your standardized administrative email signature.",
                "service_link": None,
                "doc_url": "https://docs.numerique.gouv.fr/docs/signature-guide/",
                "validation_type": ValidationTypeChoices.SIGNATURE,
            },
        )

        # 3. Colleagues
        demo_colleagues = [
            ("demo-c1", "Camille Dupont (IT referent)"),
            ("demo-c2", "Isabelle Delatour (Team lead — your manager)"),
            ("demo-c3", "Karim Benali (Technical referent)"),
            ("demo-c4", "Sophie Mercier (Local HR contact)"),
            ("demo-c5", "Thomas Nguyen (Onboarding buddy)"),
            ("demo-c6", "Julie Lambert (Project manager)"),
            ("demo-c7", "Nicolas Petit (Security officer)"),
            ("demo-c8", "Amel Haddad (Communications lead)"),
            ("demo-c9", "Marc Rousseau (Facilities manager)"),
            ("demo-c10", "Elodie Bernard (Data protection officer)"),
            ("demo-c11", "Baptiste Girard (Network engineer)"),
            ("demo-c12", "Léa Fontaine (Deputy team lead)"),
            ("demo-c13", "Anna Bellanger (Internal communications officer)"),
            ("demo-c14", "Hugo Lefebvre (Office manager)"),
            ("demo-c15", "Manon Girard (Recruitment officer)"),
        ]
        tchap_demo_link = "https://claude.ai/artifact/TuLZxVo41LLtpAeoqDqwEJ"
        for row_id, full_name in demo_colleagues:
            Colleague.objects.update_or_create(
                grist_row_id=row_id,
                defaults={
                    "template": template,
                    "name": full_name,
                    "tchap_link": tchap_demo_link,
                },
            )

        # 4. Documents
        Document.objects.update_or_create(
            grist_row_id="demo-doc-first-days",
            defaults={
                "template": template,
                "title": "My first 30 days",
                "url": "https://app.notion.com/p/3de89a0c98c581fabd8ef6bc4a3c56ba",
                "format": DocumentFormatChoices.DOC,
            },
        )
        Document.objects.update_or_create(
            grist_row_id="demo-doc-environment",
            defaults={
                "template": template,
                "title": "My environment",
                "url": "https://app.notion.com/p/3de89a0c98c581ce8038c94beb36db42",
                "format": DocumentFormatChoices.DOC,
            },
        )
        Document.objects.update_or_create(
            grist_row_id="demo-doc-charte",
            defaults={
                "template": template,
                "title": "IT and security",
                "url": "https://fichiers.numerique.gouv.fr/s/charte-informatique",
                "format": DocumentFormatChoices.PDF,
            },
        )

        # 5. Training
        Training.objects.update_or_create(
            grist_row_id="demo-train-suite",
            defaults={
                "template": template,
                "title": "Getting Started with the La Suite Collaboration Tools",
                "video_url": "https://tube.numerique.gouv.fr/w/demo-la-suite",
                "duration_minutes": 15,
            },
        )

        # 6. Agents
        alex, _ = Agent.objects.update_or_create(
            email="alex.martin@gouv.fr",
            defaults={
                "name": "Alex Martin",
                "role": RoleChoices.NEW_AGENT,
                "assigned_template": template,
                "signature_accepted": False,
            },
        )

        Agent.objects.update_or_create(
            email="lea.fontaine@gouv.fr",
            defaults={
                "name": "Léa Fontaine",
                "role": RoleChoices.NEW_AGENT,
                "assigned_template": template,
                "signature_accepted": False,
            },
        )

        Agent.objects.update_or_create(
            email="camille.dupont@gouv.fr",
            defaults={
                "name": "Camille Dupont",
                "role": RoleChoices.MANAGER,
                "assigned_template": None,
                "signature_accepted": True,
            },
        )

        Agent.objects.update_or_create(
            email="robert.dupont@gouv.fr",
            defaults={
                "name": "Robert Dupont",
                "role": RoleChoices.MANAGER,
                "assigned_template": None,
                "signature_accepted": True,
            },
        )
        Agent.objects.update_or_create(
            email="Sherloc.holmes@gouv.fr",
            defaults={
                "name": "Sherloc Holmes",
                "role": RoleChoices.MANAGER,
                "assigned_template": None,
                "signature_accepted": True,
            },
        )

        # Keycloak realm demo users (from docker/keycloak/realm.json)
        kc_agent, _ = Agent.objects.update_or_create(
            email="agent@bienvenue.local",
            defaults={
                "name": "Alex Agent",
                "role": RoleChoices.NEW_AGENT,
                "assigned_template": template,
                "signature_accepted": False,
            },
        )

        Agent.objects.update_or_create(
            email="manager@bienvenue.local",
            defaults={
                "name": "Morgane Manager",
                "role": RoleChoices.MANAGER,
                "assigned_template": template,
                "signature_accepted": True,
            },
        )

        # 7. Initial Statuses for Alex Martin and Keycloak Agent
        for user_agent in [alex, kc_agent]:
            for todo in [todo_fichiers, todo_tchap, todo_signature]:
                AgentTodoStatus.objects.get_or_create(
                    agent=user_agent,
                    todo_item=todo,
                    defaults={"done": False},
                )

        self.stdout.write(self.style.SUCCESS("Demo data successfully seeded."))
