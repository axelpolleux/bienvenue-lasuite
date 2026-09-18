import uuid
from django.test import TestCase
from django.db.utils import IntegrityError
from src.onboarding.models import (
    Template,
    Agent,
    TodoItem,
    AgentTodoStatus,
    Colleague,
    Document,
    Training,
    Service,
    AgentComment,
    RoleChoices,
    ValidationTypeChoices,
    DocumentFormatChoices,
)


class OnboardingModelsTest(TestCase):
    """Test suite for onboarding ORM models and constraints."""

    def setUp(self):
        """Seed a base template and agent for model tests."""
        self.template = Template.objects.create(
            name="Socle Commun",
            grist_row_id="grist-tpl-1",
            email_signature="Cordialement, Alex Martin",
        )
        self.agent = Agent.objects.create(
            email="alex.martin@gouv.fr",
            name="Alex Martin",
            role=RoleChoices.NEW_AGENT,
            assigned_template=self.template,
        )

    def test_template_creation(self):
        """Verify Template model properties and string representation."""
        self.assertIsInstance(self.template.id, uuid.UUID)
        self.assertEqual(str(self.template), "Socle Commun (grist-tpl-1)")

    def test_agent_creation_and_defaults(self):
        """Verify Agent default fields and foreign key linkage."""
        self.assertIsInstance(self.agent.id, uuid.UUID)
        self.assertFalse(self.agent.signature_accepted)
        self.assertEqual(self.agent.assigned_template, self.template)
        self.assertEqual(str(self.agent), "Alex Martin <alex.martin@gouv.fr> (new_agent)")

    def test_agent_unique_email(self):
        """Verify unique constraint on agent email."""
        with self.assertRaises(IntegrityError):
            Agent.objects.create(
                email="alex.martin@gouv.fr",
                name="Duplicate Agent",
                role=RoleChoices.NEW_AGENT,
            )

    def test_agent_unique_email_case_insensitive(self):
        """Verify case-insensitive unique constraint on agent email."""
        with self.assertRaises(IntegrityError):
            Agent.objects.create(
                email="ALEX.MARTIN@GOUV.FR",
                name="Case Duplicate Agent",
                role=RoleChoices.NEW_AGENT,
            )

    def test_todo_item_creation(self):
        """Verify TodoItem ordering and validation type choices."""
        todo = TodoItem.objects.create(
            template=self.template,
            label="Activer compte Fichiers",
            description="Fichiers is your personal storage space.",
            doc_url="https://docs.numerique.gouv.fr/docs/fichiers/",
            service_link="https://fichiers.numerique.gouv.fr",
            order=1,
            validation_type=ValidationTypeChoices.API_CHECK,
            grist_row_id="grist-todo-1",
        )
        self.assertEqual(todo.order, 1)
        self.assertEqual(todo.validation_type, "API_CHECK")
        self.assertEqual(todo.description, "Fichiers is your personal storage space.")
        self.assertEqual(todo.doc_url, "https://docs.numerique.gouv.fr/docs/fichiers/")
        self.assertEqual(str(todo), "[1] Activer compte Fichiers (API_CHECK)")

    def test_todo_item_defaults(self):
        """Verify TodoItem default description and null doc_url."""
        todo = TodoItem.objects.create(
            template=self.template,
            label="Simple task",
            order=2,
        )
        self.assertEqual(todo.description, "")
        self.assertIsNone(todo.doc_url)

    def test_agent_todo_status_unique_constraint(self):
        """Verify AgentTodoStatus uniqueness per (agent, todo_item)."""
        todo = TodoItem.objects.create(
            template=self.template,
            label="Task 1",
            order=1,
            validation_type=ValidationTypeChoices.MANUAL,
        )
        status = AgentTodoStatus.objects.create(
            agent=self.agent,
            todo_item=todo,
            done=False,
        )
        self.assertFalse(status.done)
        with self.assertRaises(IntegrityError):
            AgentTodoStatus.objects.create(
                agent=self.agent,
                todo_item=todo,
                done=True,
            )

    def test_colleague_creation(self):
        """Verify Colleague creation linked to template."""
        colleague = Colleague.objects.create(
            template=self.template,
            name="Camille Dupont",
            tchap_link="https://tchap.gouv.fr/#/user/@camille:agent.gouv.fr",
            grist_row_id="grist-col-1",
        )
        self.assertEqual(str(colleague), "Camille Dupont")

    def test_document_creation(self):
        """Verify Document creation with format choices."""
        doc = Document.objects.create(
            template=self.template,
            title="Charte Informatique",
            url="https://fichiers.numerique.gouv.fr/s/charte",
            format=DocumentFormatChoices.PDF,
            grist_row_id="grist-doc-1",
        )
        self.assertEqual(doc.format, "pdf")
        self.assertEqual(str(doc), "Charte Informatique (pdf)")

    def test_training_creation(self):
        """Verify Training creation with duration."""
        training = Training.objects.create(
            template=self.template,
            title="Tutoriel Tchap",
            video_url="https://tube.numerique.gouv.fr/w/123",
            duration_minutes=10,
            grist_row_id="grist-train-1",
        )
        self.assertEqual(training.duration_minutes, 10)
        self.assertEqual(str(training), "Tutoriel Tchap (10 min)")

    def test_service_creation(self):
        """Verify Service model creation and defaults."""
        service = Service.objects.create(
            name="Direction du Numérique",
            initials="DN",
            color="#000091",
            manager_name="Camille Dupont",
            manager_email="camille.dupont@gouv.fr",
            default_template=self.template,
            grist_row_id="grist-svc-1",
        )
        self.assertIsInstance(service.id, uuid.UUID)
        self.assertEqual(str(service), "Direction du Numérique (DN)")
        self.assertEqual(service.default_template, self.template)

    def test_agent_profile_fields_and_service(self):
        """Verify Agent extra profile fields, service link, and colleagues_to_meet."""
        service = Service.objects.create(
            name="Direction du Numérique",
            initials="DN",
            color="#000091",
            grist_row_id="grist-svc-2",
        )
        colleague_agent = Agent.objects.create(
            email="lea.fontaine@gouv.fr",
            name="Léa Fontaine",
            role=RoleChoices.NEW_AGENT,
        )
        self.agent.job_title = "Chargé de mission numérique"
        self.agent.phone = "01 40 00 00 27"
        self.agent.service = service
        self.agent.save()
        self.agent.colleagues_to_meet.add(colleague_agent)

        self.agent.refresh_from_db()
        self.assertEqual(self.agent.job_title, "Chargé de mission numérique")
        self.assertEqual(self.agent.phone, "01 40 00 00 27")
        self.assertEqual(self.agent.service, service)
        self.assertIn(colleague_agent, self.agent.colleagues_to_meet.all())

    def test_agent_comment_creation(self):
        """Verify AgentComment model creation linked to an Agent."""
        comment = AgentComment.objects.create(
            agent=self.agent,
            text="Excellente progression sur l'onboarding.",
            grist_row_id="grist-comm-1",
        )
        self.assertIsInstance(comment.id, uuid.UUID)
        self.assertEqual(comment.agent, self.agent)
        self.assertIn("Excellente progression", str(comment))
