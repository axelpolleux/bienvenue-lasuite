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
            service_link="https://fichiers.numerique.gouv.fr",
            order=1,
            validation_type=ValidationTypeChoices.API_CHECK,
            grist_row_id="grist-todo-1",
        )
        self.assertEqual(todo.order, 1)
        self.assertEqual(todo.validation_type, "API_CHECK")
        self.assertEqual(str(todo), "[1] Activer compte Fichiers (API_CHECK)")

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
