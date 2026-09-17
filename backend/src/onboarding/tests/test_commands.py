from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from src.onboarding.models import Agent, Template, TodoItem


class SeedDemoDataCommandTest(TestCase):
    """Test seed_demo_data management command."""

    def test_seed_demo_data_execution(self):
        """Verify command seeds template, agent, and tasks idempotently."""
        out = StringIO()
        call_command("seed_demo_data", stdout=out)
        self.assertIn("Demo data successfully seeded", out.getvalue())

        self.assertTrue(Template.objects.filter(grist_row_id="demo-template-core").exists())
        self.assertTrue(Agent.objects.filter(email="alex.martin@gouv.fr").exists())
        self.assertTrue(Agent.objects.filter(email="camille.dupont@gouv.fr").exists())
        self.assertTrue(Agent.objects.filter(email="agent@bienvenue.local").exists())
        self.assertTrue(Agent.objects.filter(email="manager@bienvenue.local").exists())
        self.assertIsNotNone(Agent.objects.get(email="agent@bienvenue.local").assigned_template)
        self.assertIsNotNone(Agent.objects.get(email="manager@bienvenue.local").assigned_template)

        self.assertGreaterEqual(TodoItem.objects.count(), 3)
        todo = TodoItem.objects.get(grist_row_id="demo-todo-fichiers")
        self.assertTrue(todo.description)
        self.assertTrue(todo.doc_url)

        # Run again to verify idempotency
        call_command("seed_demo_data", stdout=out)
        self.assertEqual(Agent.objects.filter(email="alex.martin@gouv.fr").count(), 1)
        self.assertEqual(Agent.objects.filter(email="agent@bienvenue.local").count(), 1)


class ResetOnboardingCommandTest(TestCase):
    """Test reset_onboarding management command."""

    def setUp(self):
        call_command("seed_demo_data", stdout=StringIO())
        self.alex = Agent.objects.get(email="alex.martin@gouv.fr")
        self.alex.signature_accepted = True
        self.alex.save()
        self.alex.todo_statuses.update(done=True)

    def test_reset_all_new_agents(self):
        """Verify resetting all new agents resets tasks and signature."""
        out = StringIO()
        call_command("reset_onboarding", stdout=out)
        self.assertIn("Successfully reset onboarding progress", out.getvalue())

        self.alex.refresh_from_db()
        self.assertFalse(self.alex.signature_accepted)
        self.assertFalse(self.alex.todo_statuses.filter(done=True).exists())

    def test_reset_specific_agent(self):
        """Verify resetting a specific agent by email."""
        out = StringIO()
        call_command("reset_onboarding", agent="alex.martin@gouv.fr", stdout=out)
        self.assertIn("Reset alex.martin@gouv.fr", out.getvalue())

        self.alex.refresh_from_db()
        self.assertFalse(self.alex.signature_accepted)
        self.assertFalse(self.alex.todo_statuses.filter(done=True).exists())

    def test_reset_nonexistent_agent_raises_error(self):
        """Verify command errors if invalid email is provided."""
        from django.core.management.base import CommandError
        with self.assertRaises(CommandError):
            call_command("reset_onboarding", agent="nonexistent@gouv.fr")

