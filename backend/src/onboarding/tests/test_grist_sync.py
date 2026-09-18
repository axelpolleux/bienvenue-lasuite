from django.test import TestCase
from unittest.mock import patch
from src.onboarding.models import Agent, RoleChoices, Template, Service, AgentComment
from src.onboarding.services.grist_sync import (
    sync_members,
    sync_services,
    sync_comments,
)


class SyncMembersTest(TestCase):
    """Test suite for provisioning agents from the Grist Members table."""

    def setUp(self):
        self.template = Template.objects.create(
            name="Onboarding RH", grist_row_id="10"
        )

    def test_creates_new_agent_with_template(self):
        records = [
            {
                "id": 1,
                "fields": {
                    "Email": "Lara.Clette@gouv.fr",
                    "Name": "Lara Clette",
                    "Template": 10,
                },
            }
        ]
        synced = sync_members(records)
        self.assertEqual(synced, 1)

        agent = Agent.objects.get(email="lara.clette@gouv.fr")
        self.assertEqual(agent.name, "Lara Clette")
        self.assertEqual(agent.role, RoleChoices.NEW_AGENT)
        self.assertEqual(agent.assigned_template, self.template)

    def test_updates_existing_agent_template(self):
        agent = Agent.objects.create(
            email="lara.clette@gouv.fr", name="Old Name", role=RoleChoices.NEW_AGENT
        )
        records = [
            {
                "id": 1,
                "fields": {"Email": "lara.clette@gouv.fr", "Name": "Lara Clette", "Template": 10},
            }
        ]
        sync_members(records)

        agent.refresh_from_db()
        self.assertEqual(agent.name, "Lara Clette")
        self.assertEqual(agent.assigned_template, self.template)

    def test_never_downgrades_an_existing_manager(self):
        manager = Agent.objects.create(
            email="eric.hochet@gouv.fr", name="Eric Hochet", role=RoleChoices.MANAGER
        )
        records = [
            {
                "id": 2,
                "fields": {"Email": "eric.hochet@gouv.fr", "Name": "Eric Hochet", "Template": 10},
            }
        ]
        sync_members(records)

        manager.refresh_from_db()
        self.assertEqual(manager.role, RoleChoices.MANAGER)

    def test_skips_rows_with_no_email(self):
        records = [{"id": 1, "fields": {"Name": "No Email", "Template": 10}}]
        synced = sync_members(records)
        self.assertEqual(synced, 0)
        self.assertFalse(Agent.objects.filter(name="No Email").exists())

    def test_sync_members_with_profile_attributes_and_service(self):
        service = Service.objects.create(
            name="Direction du Numérique",
            initials="DN",
            grist_row_id="1",
        )
        records = [
            {
                "id": 10,
                "fields": {
                    "Email": "alex.martin@gouv.fr",
                    "Name": "Alex Martin",
                    "Role": "Chargé de mission numérique",
                    "Phone": "01 40 00 00 27",
                    "Service": 1,
                    "ArrivalDate": 1788220800,
                    "Template": 10,
                    "ColleaguesToMeet": ["L", 11],
                },
            },
            {
                "id": 11,
                "fields": {
                    "Email": "lea.fontaine@gouv.fr",
                    "Name": "Léa Fontaine",
                    "Role": "Développeuse",
                    "Service": 1,
                    "Template": 10,
                },
            },
        ]
        sync_members(records)

        alex = Agent.objects.get(email="alex.martin@gouv.fr")
        self.assertEqual(alex.job_title, "Chargé de mission numérique")
        self.assertEqual(alex.phone, "01 40 00 00 27")
        self.assertEqual(alex.service, service)
        self.assertIsNotNone(alex.arrival_date)

        lea = Agent.objects.get(email="lea.fontaine@gouv.fr")
        self.assertIn(lea, alex.colleagues_to_meet.all())


class SyncTodoItemsTest(TestCase):
    """Test suite for syncing todo items with Kind and ValidationType mappings."""

    def setUp(self):
        self.template = Template.objects.create(
            name="Onboarding Numérique", grist_row_id="20"
        )

    def test_sync_todo_items_with_kind_mapping(self):
        from src.onboarding.models import TodoItem, ValidationTypeChoices
        from src.onboarding.services.grist_sync import sync_todo_items

        records = [
            {
                "id": 101,
                "fields": {
                    "Label": "Configurer messagerie",
                    "Description": "Configuration mail",
                    "Kind": "MANUEL",
                    "Order": 1,
                    "Template": 20,
                },
            },
            {
                "id": 102,
                "fields": {
                    "Label": "Valider la signature email",
                    "Description": "Génération de signature",
                    "Kind": "AUTO",
                    "Order": 2,
                    "Template": 20,
                },
            },
            {
                "id": 103,
                "fields": {
                    "Label": "Activer espace Fichiers",
                    "Description": "Vérification Fichiers",
                    "Kind": "AUTO",
                    "Order": 3,
                    "Template": 20,
                },
            },
        ]
        synced = sync_todo_items(records)
        self.assertEqual(synced, 3)

        manual_item = TodoItem.objects.get(grist_row_id="101")
        self.assertEqual(manual_item.validation_type, ValidationTypeChoices.MANUAL)

        sig_item = TodoItem.objects.get(grist_row_id="102")
        self.assertEqual(sig_item.validation_type, ValidationTypeChoices.SIGNATURE)

        auto_item = TodoItem.objects.get(grist_row_id="103")
        self.assertEqual(auto_item.validation_type, ValidationTypeChoices.API_CHECK)


class PushProgressToGristTest(TestCase):
    """Test suite for pushing agent todo progress back to Grist MemberChecklist."""

    def setUp(self):
        from src.onboarding.models import AgentTodoStatus, TodoItem
        self.template = Template.objects.create(
            name="Onboarding RH", grist_row_id="10"
        )
        self.agent = Agent.objects.create(
            email="camille.dupont@gouv.fr",
            name="Camille Dupont",
            role=RoleChoices.NEW_AGENT,
            assigned_template=self.template,
        )
        self.item1 = TodoItem.objects.create(
            template=self.template,
            label="Task 1",
            order=1,
            grist_row_id="501",
        )
        self.item2 = TodoItem.objects.create(
            template=self.template,
            label="Task 2",
            order=2,
            grist_row_id="502",
        )

    def test_updates_existing_member_checklist_row(self):
        from unittest.mock import patch
        from django.utils import timezone
        from src.onboarding.models import AgentTodoStatus
        from src.onboarding.services.grist_sync import push_progress_to_grist

        now = timezone.now()
        AgentTodoStatus.objects.create(
            agent=self.agent, todo_item=self.item1, done=True, done_at=now
        )

        def mock_list(table):
            if table == "Members":
                return [{"id": 1, "fields": {"Email": "camille.dupont@gouv.fr"}}]
            if table == "MemberChecklist":
                return [
                    {"id": 901, "fields": {"Member": 1, "Item": 501, "Done": False}},
                    {"id": 902, "fields": {"Member": 1, "Item": 502, "Done": False}},
                ]
            return []

        with patch("src.onboarding.services.grist_sync.client") as mock_client:
            mock_client.list_records_safe.side_effect = mock_list
            results = push_progress_to_grist()

            self.assertEqual(results["updated"], 1)
            self.assertEqual(results["created"], 0)
            self.assertEqual(results["members_affected"], 1)
            mock_client.update_records.assert_called_once()
            args, _ = mock_client.update_records.call_args
            self.assertEqual(args[0], "MemberChecklist")
            self.assertEqual(args[1][0]["id"], 901)
            self.assertTrue(args[1][0]["fields"]["Done"])

    def test_creates_missing_member_checklist_row(self):
        from unittest.mock import patch
        from django.utils import timezone
        from src.onboarding.models import AgentTodoStatus
        from src.onboarding.services.grist_sync import push_progress_to_grist

        now = timezone.now()
        AgentTodoStatus.objects.create(
            agent=self.agent, todo_item=self.item2, done=True, done_at=now
        )

        def mock_list(table):
            if table == "Members":
                return [{"id": 1, "fields": {"Email": "camille.dupont@gouv.fr"}}]
            if table == "MemberChecklist":
                return [{"id": 901, "fields": {"Member": 1, "Item": 501, "Done": False}}]
            return []

        with patch("src.onboarding.services.grist_sync.client") as mock_client:
            mock_client.list_records_safe.side_effect = mock_list
            results = push_progress_to_grist()

            self.assertEqual(results["updated"], 0)
            self.assertEqual(results["created"], 1)
            self.assertEqual(results["members_affected"], 1)
            mock_client.create_records.assert_called_once()
            args, _ = mock_client.create_records.call_args
            self.assertEqual(args[0], "MemberChecklist")
            self.assertEqual(args[1][0]["Member"], 1)
            self.assertEqual(args[1][0]["Item"], 502)
            self.assertTrue(args[1][0]["Done"])

    def test_pushing_untoggled_tasks_creates_rows_with_done_false(self):
        """Verify that template tasks without an AgentTodoStatus are pushed with Done=False."""
        from unittest.mock import patch
        from src.onboarding.services.grist_sync import push_progress_to_grist

        def mock_list(table):
            if table == "Members":
                return [{"id": 1, "fields": {"Email": "camille.dupont@gouv.fr"}}]
            if table == "MemberChecklist":
                return []
            return []

        with patch("src.onboarding.services.grist_sync.client") as mock_client:
            mock_client.list_records_safe.side_effect = mock_list
            results = push_progress_to_grist()

            self.assertEqual(results["updated"], 0)
            self.assertEqual(results["created"], 2)
            self.assertEqual(results["members_affected"], 1)
            mock_client.create_records.assert_called_once()
            args, _ = mock_client.create_records.call_args
            self.assertEqual(args[0], "MemberChecklist")
            created_records = args[1]
            self.assertEqual(len(created_records), 2)
            for rec in created_records:
                self.assertEqual(rec["Member"], 1)
                self.assertFalse(rec["Done"])
                self.assertIsNone(rec["DoneAt"])
            items = {rec["Item"] for rec in created_records}
            self.assertEqual(items, {501, 502})

    def test_unchecking_task_updates_done_to_false(self):
        """Verify that when a task is unchecked in Postgres, Done is updated to False in Grist."""
        from unittest.mock import patch
        from src.onboarding.models import AgentTodoStatus
        from src.onboarding.services.grist_sync import push_progress_to_grist

        AgentTodoStatus.objects.create(
            agent=self.agent, todo_item=self.item1, done=False, done_at=None
        )

        def mock_list(table):
            if table == "Members":
                return [{"id": 1, "fields": {"Email": "camille.dupont@gouv.fr"}}]
            if table == "MemberChecklist":
                return [
                    {"id": 901, "fields": {"Member": 1, "Item": 501, "Done": True, "DoneAt": "2026-09-17"}},
                    {"id": 902, "fields": {"Member": 1, "Item": 502, "Done": False}},
                ]
            return []

        with patch("src.onboarding.services.grist_sync.client") as mock_client:
            mock_client.list_records_safe.side_effect = mock_list
            results = push_progress_to_grist()

            self.assertEqual(results["updated"], 1)
            self.assertEqual(results["created"], 0)
            self.assertEqual(results["members_affected"], 1)
            mock_client.update_records.assert_called_once()
            args, _ = mock_client.update_records.call_args
            self.assertEqual(args[0], "MemberChecklist")
            self.assertEqual(args[1][0]["id"], 901)
            self.assertFalse(args[1][0]["fields"]["Done"])
            self.assertIsNone(args[1][0]["fields"]["DoneAt"])

    def test_idempotent_runs_produce_no_changes(self):
        """Verify that when Grist already matches Postgres state, 0 updates and 0 creations occur."""
        from unittest.mock import patch
        from django.utils import timezone
        from src.onboarding.models import AgentTodoStatus
        from src.onboarding.services.grist_sync import push_progress_to_grist

        now = timezone.now()
        AgentTodoStatus.objects.create(
            agent=self.agent, todo_item=self.item1, done=True, done_at=now
        )

        def mock_list(table):
            if table == "Members":
                return [{"id": 1, "fields": {"Email": "camille.dupont@gouv.fr"}}]
            if table == "MemberChecklist":
                return [
                    {"id": 901, "fields": {"Member": 1, "Item": 501, "Done": True, "DoneAt": now.date().isoformat()}},
                    {"id": 902, "fields": {"Member": 1, "Item": 502, "Done": False, "DoneAt": None}},
                ]
            return []

        with patch("src.onboarding.services.grist_sync.client") as mock_client:
            mock_client.list_records_safe.side_effect = mock_list
            results = push_progress_to_grist()

            self.assertEqual(results["updated"], 0)
            self.assertEqual(results["created"], 0)
            self.assertEqual(results["members_affected"], 0)
            mock_client.update_records.assert_not_called()
            mock_client.create_records.assert_not_called()


class SyncServicesTest(TestCase):
    def setUp(self):
        self.template = Template.objects.create(
            name="Onboarding DN", grist_row_id="2"
        )

    def test_sync_services_creates_and_updates_service(self):
        records = [
            {
                "id": 1,
                "fields": {
                    "Name": "Direction du Numérique",
                    "Initials": "DN",
                    "Color": "#000091",
                    "LogoURL": "https://example.com/logo.png",
                    "Manager": "Camille Dupont",
                    "ManagerEmail": "camille.dupont@gouv.fr",
                    "DefaultTemplate": 2,
                },
            }
        ]
        synced = sync_services(records)
        self.assertEqual(synced, 1)

        svc = Service.objects.get(grist_row_id="1")
        self.assertEqual(svc.name, "Direction du Numérique")
        self.assertEqual(svc.initials, "DN")
        self.assertEqual(svc.color, "#000091")
        self.assertEqual(svc.manager_name, "Camille Dupont")
        self.assertEqual(svc.manager_email, "camille.dupont@gouv.fr")
        self.assertEqual(svc.default_template, self.template)


class SyncCommentsTest(TestCase):
    def setUp(self):
        self.agent = Agent.objects.create(
            email="camille.dupont@gouv.fr",
            name="Camille Dupont",
        )

    def test_sync_comments_associates_with_agent(self):
        with patch("src.onboarding.services.grist_sync.client") as mock_client:
            mock_client.list_records_safe.return_value = [
                {"id": 1, "fields": {"Email": "camille.dupont@gouv.fr"}}
            ]
            records = [
                {
                    "id": 101,
                    "fields": {
                        "Member": 1,
                        "Date": 1788307200,
                        "Text": "Référente pour l'onboarding technique.",
                    },
                }
            ]
            synced = sync_comments(records)
            self.assertEqual(synced, 1)

            comment = AgentComment.objects.get(grist_row_id="101")
            self.assertEqual(comment.agent, self.agent)
            self.assertEqual(comment.text, "Référente pour l'onboarding technique.")
            self.assertIsNotNone(comment.date)


