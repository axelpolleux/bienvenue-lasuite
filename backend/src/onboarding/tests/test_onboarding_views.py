"""Test suite for new agent onboarding endpoints."""

import uuid
from unittest.mock import patch
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from src.onboarding.models import (

    Agent,
    AgentTodoStatus,
    RoleChoices,
    Template,
    TodoItem,
    ValidationTypeChoices,
)


@override_settings(DEBUG=True)
class OnboardingViewsTest(TestCase):
    """Test suite for new agent onboarding endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.template = Template.objects.create(
            name="Template Test",
            grist_row_id="tpl-test-1",
            email_signature="Best,\nAlex",
        )
        self.agent = Agent.objects.create(
            email="alex.martin@gouv.fr",
            name="Alex Martin",
            role=RoleChoices.NEW_AGENT,
            assigned_template=self.template,
        )
        self.todo1 = TodoItem.objects.create(
            template=self.template,
            label="Step 1: Fichiers",
            order=1,
            validation_type=ValidationTypeChoices.API_CHECK,
        )
        self.todo2 = TodoItem.objects.create(
            template=self.template,
            label="Step 2: Tchap",
            order=2,
            validation_type=ValidationTypeChoices.MANUAL,
        )

        # Other template for ownership / boundary testing
        self.other_template = Template.objects.create(
            name="Other Template",
            grist_row_id="tpl-other-2",
        )
        self.other_todo = TodoItem.objects.create(
            template=self.other_template,
            label="Foreign Todo",
            order=1,
            validation_type=ValidationTypeChoices.MANUAL,
        )

    # -------------------------------------------------------------------------
    # GET /api/onboarding/me/
    # -------------------------------------------------------------------------

    def test_get_onboarding_me_unauthorized(self):
        """Verify 401 Unauthorized when no credentials sent."""
        response = self.client.get("/api/onboarding/me/")
        self.assertEqual(response.status_code, 401)

    def test_get_onboarding_me_success(self):
        """Verify 200 OK returning full onboarding bundle."""
        response = self.client.get(
            "/api/onboarding/me/",
            HTTP_X_DEV_USER_EMAIL="alex.martin@gouv.fr",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["agent"]["email"], "alex.martin@gouv.fr")
        self.assertEqual(data["template"]["name"], "Template Test")
        self.assertEqual(len(data["todos"]), 2)

    def test_get_onboarding_me_no_agent_profile(self):
        """Verify 404 when authenticated user has no linked agent profile."""
        user = User.objects.create_user(username="orphan_user", password="secret")
        self.client.force_authenticate(user=user)
        response = self.client.get("/api/onboarding/me/")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

    # -------------------------------------------------------------------------
    # POST /api/todos/{id}/verify/
    # -------------------------------------------------------------------------

    def test_verify_todo_unauthorized(self):
        """Verify 401 Unauthorized when attempting verify without credentials."""
        response = self.client.post(f"/api/todos/{self.todo1.id}/verify/")
        self.assertEqual(response.status_code, 401)

    @patch("src.onboarding.views.onboarding.check_user_fichiers")
    def test_verify_todo_step1_success(self, mock_verifier):
        """Verify automated service verification marks task done and returns 200."""
        mock_verifier.return_value = (True, None)

        response = self.client.post(
            f"/api/todos/{self.todo1.id}/verify/",
            HTTP_X_DEV_USER_EMAIL="alex.martin@gouv.fr",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["done"])
        self.assertEqual(data["todo_id"], str(self.todo1.id))
        self.assertIn("done_at", data)

        status = AgentTodoStatus.objects.get(agent=self.agent, todo_item=self.todo1)
        self.assertTrue(status.done)
        self.assertIsNotNone(status.done_at)

    @patch("src.onboarding.views.onboarding.check_user_fichiers")
    def test_verify_todo_step1_service_failure(self, mock_verifier):
        """Verify 400 response when external service verification fails."""
        mock_verifier.return_value = (False, "User not found")

        response = self.client.post(
            f"/api/todos/{self.todo1.id}/verify/",
            HTTP_X_DEV_USER_EMAIL="alex.martin@gouv.fr",
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["done"])
        self.assertIn("error", data)

    def test_verify_todo_not_found(self):
        """Verify 404 when verifying a nonexistent todo ID."""
        random_id = uuid.uuid4()
        response = self.client.post(
            f"/api/todos/{random_id}/verify/",
            HTTP_X_DEV_USER_EMAIL="alex.martin@gouv.fr",
        )
        self.assertEqual(response.status_code, 404)

    def test_verify_todo_foreign_template_ownership_forbidden(self):
        """Verify 404 when verifying a todo belonging to another template."""
        response = self.client.post(
            f"/api/todos/{self.other_todo.id}/verify/",
            HTTP_X_DEV_USER_EMAIL="alex.martin@gouv.fr",
        )
        self.assertEqual(response.status_code, 404)

    def test_verify_todo_agent_without_template(self):
        """Verify 400 when agent has no template assigned."""
        Agent.objects.create(
            email="no.template@gouv.fr",
            name="No Template",
            role=RoleChoices.NEW_AGENT,
            assigned_template=None,
        )
        response = self.client.post(
            f"/api/todos/{self.todo1.id}/verify/",
            HTTP_X_DEV_USER_EMAIL="no.template@gouv.fr",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_verify_todo_no_agent_profile(self):
        """Verify 404 when authenticated user has no linked agent profile."""
        user = User.objects.create_user(username="orphan_verifier", password="secret")
        self.client.force_authenticate(user=user)
        response = self.client.post(f"/api/todos/{self.todo1.id}/verify/")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

    # -------------------------------------------------------------------------
    # POST /api/todos/{id}/toggle/
    # -------------------------------------------------------------------------

    def test_toggle_manual_todo_unauthorized(self):
        """Verify 401 Unauthorized when attempting toggle without credentials."""
        response = self.client.post(
            f"/api/todos/{self.todo2.id}/toggle/",
            data={"done": True},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_toggle_manual_todo_success(self):
        """Verify manual toggle endpoint updates status."""
        response = self.client.post(
            f"/api/todos/{self.todo2.id}/toggle/",
            data={"done": True},
            content_type="application/json",
            HTTP_X_DEV_USER_EMAIL="alex.martin@gouv.fr",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["done"])

        status = AgentTodoStatus.objects.get(agent=self.agent, todo_item=self.todo2)
        self.assertTrue(status.done)
        self.assertIsNotNone(status.done_at)

    def test_toggle_manual_todo_default_done(self):
        """Verify toggle without explicit done payload defaults to True."""
        response = self.client.post(
            f"/api/todos/{self.todo2.id}/toggle/",
            content_type="application/json",
            HTTP_X_DEV_USER_EMAIL="alex.martin@gouv.fr",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["done"])

        status = AgentTodoStatus.objects.get(agent=self.agent, todo_item=self.todo2)
        self.assertTrue(status.done)

    def test_toggle_manual_todo_unmark(self):
        """Verify toggling with done=False unmarks the item and clears done_at."""
        AgentTodoStatus.objects.create(
            agent=self.agent,
            todo_item=self.todo2,
            done=True,
        )
        response = self.client.post(
            f"/api/todos/{self.todo2.id}/toggle/",
            data={"done": False},
            content_type="application/json",
            HTTP_X_DEV_USER_EMAIL="alex.martin@gouv.fr",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["done"])
        self.assertIsNone(data["done_at"])

        status = AgentTodoStatus.objects.get(agent=self.agent, todo_item=self.todo2)
        self.assertFalse(status.done)
        self.assertIsNone(status.done_at)

    def test_toggle_todo_foreign_template_ownership_forbidden(self):
        """Verify 404 when toggling a todo belonging to another template."""
        response = self.client.post(
            f"/api/todos/{self.other_todo.id}/toggle/",
            data={"done": True},
            content_type="application/json",
            HTTP_X_DEV_USER_EMAIL="alex.martin@gouv.fr",
        )
        self.assertEqual(response.status_code, 404)

    def test_toggle_todo_agent_without_template(self):
        """Verify 400 when agent has no template assigned."""
        Agent.objects.create(
            email="no.template2@gouv.fr",
            name="No Template 2",
            role=RoleChoices.NEW_AGENT,
            assigned_template=None,
        )
        response = self.client.post(
            f"/api/todos/{self.todo2.id}/toggle/",
            data={"done": True},
            content_type="application/json",
            HTTP_X_DEV_USER_EMAIL="no.template2@gouv.fr",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_toggle_todo_no_agent_profile(self):
        """Verify 404 when authenticated user has no linked agent profile."""
        user = User.objects.create_user(username="orphan_toggler", password="secret")
        self.client.force_authenticate(user=user)
        response = self.client.post(
            f"/api/todos/{self.todo2.id}/toggle/",
            data={"done": True},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

    # -------------------------------------------------------------------------
    # POST /api/signature/accept/
    # -------------------------------------------------------------------------

    def test_accept_signature_unauthorized(self):
        """Verify 401 Unauthorized when accepting signature without credentials."""
        response = self.client.post("/api/signature/accept/")
        self.assertEqual(response.status_code, 401)

    def test_accept_signature_success(self):
        """Verify signature acceptance endpoint sets signature_accepted=True."""
        self.assertFalse(self.agent.signature_accepted)
        response = self.client.post(
            "/api/signature/accept/",
            HTTP_X_DEV_USER_EMAIL="alex.martin@gouv.fr",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["signature_accepted"])

        self.agent.refresh_from_db()
        self.assertTrue(self.agent.signature_accepted)

    def test_accept_signature_no_agent_profile(self):
        """Verify 404 when authenticated user has no linked agent profile."""
        user = User.objects.create_user(username="orphan_signer", password="secret")
        self.client.force_authenticate(user=user)
        response = self.client.post("/api/signature/accept/")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())
