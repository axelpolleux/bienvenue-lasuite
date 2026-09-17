from django.test import TestCase
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
from src.onboarding.serializers import (
    TemplateSerializer,
    ColleagueSerializer,
    DocumentSerializer,
    TrainingSerializer,
    AgentSerializer,
    TodoItemWithStatusSerializer,
    OnboardingBundleSerializer,
    ManagerAgentOverviewSerializer,
)


class SerializersTest(TestCase):
    """Test suite for DRF serializers and computed fields."""

    def setUp(self):
        """Setup template, agent, tasks, and resources."""
        self.template = Template.objects.create(
            name="Template DSI",
            grist_row_id="grist-1",
            email_signature="Best regards,\nAlex Martin",
        )
        self.agent = Agent.objects.create(
            email="alex.martin@gouv.fr",
            name="Alex Martin",
            role=RoleChoices.NEW_AGENT,
            assigned_template=self.template,
        )
        self.todo1 = TodoItem.objects.create(
            template=self.template,
            label="Step 1: Check Fichiers",
            order=1,
            validation_type=ValidationTypeChoices.API_CHECK,
            service_link="https://fichiers.gouv.fr",
        )
        self.todo2 = TodoItem.objects.create(
            template=self.template,
            label="Step 2: Join Tchap",
            order=2,
            validation_type=ValidationTypeChoices.MANUAL,
        )
        self.status1 = AgentTodoStatus.objects.create(
            agent=self.agent,
            todo_item=self.todo1,
            done=True,
        )
        self.status2 = AgentTodoStatus.objects.create(
            agent=self.agent,
            todo_item=self.todo2,
            done=False,
        )
        self.colleague = Colleague.objects.create(
            template=self.template,
            name="Camille Dupont",
            tchap_link="https://tchap.gouv.fr/#/user/@camille:gouv.fr",
        )
        self.document = Document.objects.create(
            template=self.template,
            title="Charte Sécurité",
            url="https://fichiers.gouv.fr/doc.pdf",
            format=DocumentFormatChoices.PDF,
        )
        self.training = Training.objects.create(
            template=self.template,
            title="Tuto Visio",
            video_url="https://tube.gouv.fr/visio",
            duration_minutes=15,
        )

    def test_template_serializer(self):
        """Verify Template serialization."""
        data = TemplateSerializer(self.template).data
        self.assertEqual(data["name"], "Template DSI")
        self.assertEqual(data["email_signature"], "Best regards,\nAlex Martin")

    def test_agent_serializer_with_progress(self):
        """Verify Agent serialization includes computed progress."""
        data = AgentSerializer(self.agent).data
        self.assertEqual(data["email"], "alex.martin@gouv.fr")
        self.assertEqual(data["progress"]["total_tasks"], 2)
        self.assertEqual(data["progress"]["completed_tasks"], 1)
        self.assertEqual(data["progress"]["percentage"], 50)

    def test_todo_item_with_status_serializer(self):
        """Verify task serialization calculates locked state correctly."""
        self.todo1.description = "Check your storage space."
        self.todo1.doc_url = "https://docs.numerique.gouv.fr/docs/fichiers/"
        self.todo1.save()

        data = TodoItemWithStatusSerializer(
            self.todo1,
            context={"agent": self.agent},
        ).data
        self.assertTrue(data["done"])
        self.assertFalse(data["is_locked"])
        self.assertEqual(data["description"], "Check your storage space.")
        self.assertEqual(data["doc_url"], "https://docs.numerique.gouv.fr/docs/fichiers/")
        self.assertEqual(data["service_name"], "Fichiers")

        data2 = TodoItemWithStatusSerializer(
            self.todo2,
            context={"agent": self.agent},
        ).data
        self.assertFalse(data2["done"])
        # Step 1 is done, so Step 2 is unlocked
        self.assertFalse(data2["is_locked"])
        self.assertEqual(data2["service_name"], "Tchap")

    def test_todo_item_service_name_mapping(self):
        """Verify get_service_name recognizes required Suite services."""
        services = [
            ("https://docs.numerique.gouv.fr", "Write docs", "Docs"),
            ("https://tchap.gouv.fr", "Join Tchap", "Tchap"),
            ("https://fichiers.numerique.gouv.fr", "Store files", "Fichiers"),
            ("https://webinaire.numerique.gouv.fr", "Online webinar", "Webinaire"),
            ("https://visio.numerique.gouv.fr", "Video call", "Visio"),
            ("https://grist.numerique.gouv.fr", "Data table", "Grist"),
            ("https://francetransfert.numerique.gouv.fr", "Send files", "France Transfert"),
            ("https://custom.tool.local", "Internal Tool", "Service"),
            (None, "Generic task without link", "Service"),
        ]
        for link, label, expected_service in services:
            item = TodoItem.objects.create(
                template=self.template,
                label=label,
                service_link=link,
                order=10,
            )
            data = TodoItemWithStatusSerializer(item, context={"agent": self.agent}).data
            self.assertEqual(data["service_name"], expected_service)

    def test_onboarding_bundle_serializer(self):
        """Verify root onboarding bundle serialization matches API spec."""
        bundle_data = OnboardingBundleSerializer(
            self.agent,
            context={"agent": self.agent},
        ).data
        self.assertIn("agent", bundle_data)
        self.assertIn("template", bundle_data)
        self.assertIn("todos", bundle_data)
        self.assertIn("colleagues", bundle_data)
        self.assertIn("documents", bundle_data)
        self.assertIn("trainings", bundle_data)
        self.assertEqual(len(bundle_data["todos"]), 2)
        self.assertEqual(len(bundle_data["colleagues"]), 1)
        self.assertEqual(len(bundle_data["documents"]), 1)
        self.assertEqual(len(bundle_data["trainings"]), 1)

    def test_manager_agent_overview_serializer(self):
        """Verify manager overview serialization."""
        data = ManagerAgentOverviewSerializer(self.agent).data
        self.assertEqual(data["name"], "Alex Martin")
        self.assertEqual(data["email"], "alex.martin@gouv.fr")
        self.assertEqual(data["template_name"], "Template DSI")
        self.assertEqual(data["progress_percentage"], 50)
        self.assertEqual(data["current_step"], "Step 2: Join Tchap")

    def test_agent_serializer_without_assigned_template(self):
        """Verify Agent serialization returns zeroes when no template is assigned."""
        agent = Agent.objects.create(
            email="notemplate@gouv.fr",
            name="No Template Agent",
            role=RoleChoices.NEW_AGENT,
            assigned_template=None,
        )
        data = AgentSerializer(agent).data
        self.assertEqual(data["progress"]["total_tasks"], 0)
        self.assertEqual(data["progress"]["completed_tasks"], 0)
        self.assertEqual(data["progress"]["percentage"], 0)

    def test_agent_serializer_with_empty_template(self):
        """Verify Agent serialization handles empty template without division by zero."""
        empty_template = Template.objects.create(
            name="Empty Template",
            grist_row_id="grist-empty",
        )
        agent = Agent.objects.create(
            email="empty@gouv.fr",
            name="Empty Agent",
            role=RoleChoices.NEW_AGENT,
            assigned_template=empty_template,
        )
        data = AgentSerializer(agent).data
        self.assertEqual(data["progress"]["total_tasks"], 0)
        self.assertEqual(data["progress"]["completed_tasks"], 0)
        self.assertEqual(data["progress"]["percentage"], 100)

    def test_todo_item_is_locked_when_prior_task_incomplete(self):
        """Verify task is locked when prior sequential task is not done."""
        # Uncomplete step 1
        self.status1.done = False
        self.status1.save()

        data2 = TodoItemWithStatusSerializer(
            self.todo2,
            context={"agent": self.agent},
        ).data
        self.assertTrue(data2["is_locked"])

    def test_todo_item_without_agent_in_context(self):
        """Verify TodoItemWithStatusSerializer safely defaults when agent is omitted."""
        data = TodoItemWithStatusSerializer(self.todo1, context={}).data
        self.assertFalse(data["done"])
        self.assertIsNone(data["done_at"])
        self.assertFalse(data["is_locked"])

    def test_onboarding_bundle_serializer_without_template(self):
        """Verify root onboarding bundle serialization when agent has no template."""
        agent = Agent.objects.create(
            email="orphan@gouv.fr",
            name="Orphan Agent",
            role=RoleChoices.NEW_AGENT,
            assigned_template=None,
        )
        bundle_data = OnboardingBundleSerializer(
            agent,
            context={"agent": agent},
        ).data
        self.assertIsNone(bundle_data["template"])
        self.assertEqual(bundle_data["todos"], [])
        self.assertEqual(bundle_data["colleagues"], [])
        self.assertEqual(bundle_data["documents"], [])
        self.assertEqual(bundle_data["trainings"], [])

    def test_manager_overview_no_template_and_all_completed(self):
        """Verify manager overview for agent with no template and agent with all completed."""
        orphan = Agent.objects.create(
            email="orphan2@gouv.fr",
            name="Orphan Agent 2",
            role=RoleChoices.NEW_AGENT,
            assigned_template=None,
        )
        orphan_data = ManagerAgentOverviewSerializer(orphan).data
        self.assertIsNone(orphan_data["template_name"])
        self.assertEqual(orphan_data["progress_percentage"], 0)
        self.assertEqual(orphan_data["current_step"], "No template assigned")

        # Mark all tasks done for self.agent
        self.status2.done = True
        self.status2.save()
        completed_data = ManagerAgentOverviewSerializer(self.agent).data
        self.assertEqual(completed_data["progress_percentage"], 100)
        self.assertEqual(completed_data["current_step"], "All tasks completed")
