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
        self.assertGreaterEqual(TodoItem.objects.count(), 2)

        # Run again to verify idempotency
        call_command("seed_demo_data", stdout=out)
        self.assertEqual(Agent.objects.filter(email="alex.martin@gouv.fr").count(), 1)
