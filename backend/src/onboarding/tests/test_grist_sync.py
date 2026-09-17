from django.test import TestCase
from src.onboarding.models import Agent, RoleChoices, Template
from src.onboarding.services.grist_sync import sync_members


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
