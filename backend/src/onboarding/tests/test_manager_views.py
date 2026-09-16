"""Test suite for manager overview and template assignment endpoints."""

import uuid
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from src.onboarding.models import Agent, RoleChoices, Template


@override_settings(DEBUG=True)
class ManagerViewsTest(TestCase):
    """Test suite for manager overview and template assignment endpoints."""

    def setUp(self):
        self.client = APIClient()

        self.manager = Agent.objects.create(
            email="manager.boss@gouv.fr",
            name="Manager Boss",
            role=RoleChoices.MANAGER,
        )
        self.template1 = Template.objects.create(
            name="Template One",
            grist_row_id="tpl-row-1",
            email_signature="Signature 1",
        )
        self.template2 = Template.objects.create(
            name="Template Two",
            grist_row_id="tpl-row-2",
            email_signature="Signature 2",
        )
        self.agent = Agent.objects.create(
            email="newcomer.agent@gouv.fr",
            name="Newcomer Agent",
            role=RoleChoices.NEW_AGENT,
            assigned_template=self.template1,
        )

    # -------------------------------------------------------------------------
    # GET /api/manager/overview/
    # -------------------------------------------------------------------------

    def test_manager_overview_unauthorized(self):
        """Verify 401 Unauthorized when no auth credentials provided."""
        response = self.client.get("/api/manager/overview/")
        self.assertEqual(response.status_code, 401)

    def test_manager_overview_forbidden_for_new_agent(self):
        """Verify 403 Forbidden when authenticated as a NEW_AGENT."""
        response = self.client.get(
            "/api/manager/overview/",
            HTTP_X_DEV_USER_EMAIL=self.agent.email,
        )
        self.assertEqual(response.status_code, 403)

    def test_manager_overview_success(self):
        """Verify 200 OK when authenticated as MANAGER with newcomers list."""
        newer_agent = Agent.objects.create(
            email="newer.agent@gouv.fr",
            name="Newer Agent",
            role=RoleChoices.NEW_AGENT,
            assigned_template=self.template2,
        )

        response = self.client.get(
            "/api/manager/overview/",
            HTTP_X_DEV_USER_EMAIL=self.manager.email,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["total_newcomers"], 2)
        self.assertEqual(len(data["agents"]), 2)
        # Verify ordering by -created_at (newer_agent first)
        self.assertEqual(data["agents"][0]["id"], str(newer_agent.id))
        self.assertEqual(data["agents"][0]["email"], "newer.agent@gouv.fr")
        self.assertEqual(data["agents"][0]["template_name"], "Template Two")
        self.assertEqual(data["agents"][1]["id"], str(self.agent.id))
        self.assertEqual(data["agents"][1]["email"], "newcomer.agent@gouv.fr")
        self.assertEqual(data["agents"][1]["template_name"], "Template One")

    # -------------------------------------------------------------------------
    # PATCH /api/agents/<uuid:pk>/assign-template/
    # -------------------------------------------------------------------------

    def test_assign_template_unauthorized(self):
        """Verify 401 Unauthorized when no auth credentials provided."""
        response = self.client.patch(
            f"/api/agents/{self.agent.id}/assign-template/",
            data={"template_id": str(self.template2.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_assign_template_forbidden_for_new_agent(self):
        """Verify 403 Forbidden when authenticated as a NEW_AGENT."""
        response = self.client.patch(
            f"/api/agents/{self.agent.id}/assign-template/",
            data={"template_id": str(self.template2.id)},
            format="json",
            HTTP_X_DEV_USER_EMAIL=self.agent.email,
        )
        self.assertEqual(response.status_code, 403)

    def test_assign_template_success(self):
        """Verify 200 OK when authenticated as MANAGER and template is assigned."""
        response = self.client.patch(
            f"/api/agents/{self.agent.id}/assign-template/",
            data={"template_id": str(self.template2.id)},
            format="json",
            HTTP_X_DEV_USER_EMAIL=self.manager.email,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["agent_id"], str(self.agent.id))
        self.assertEqual(data["template_id"], str(self.template2.id))
        self.assertEqual(data["template_name"], self.template2.name)
        self.assertEqual(data["message"], "Template assigned successfully.")

        self.agent.refresh_from_db()
        self.assertEqual(self.agent.assigned_template, self.template2)

    def test_assign_template_missing_template_id(self):
        """Verify 400 Bad Request when payload lacks template_id."""
        response = self.client.patch(
            f"/api/agents/{self.agent.id}/assign-template/",
            data={},
            format="json",
            HTTP_X_DEV_USER_EMAIL=self.manager.email,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "template_id is required."})

    def test_assign_template_agent_not_found(self):
        """Verify 404 Not Found when agent UUID does not exist."""
        non_existent_agent_id = uuid.uuid4()
        response = self.client.patch(
            f"/api/agents/{non_existent_agent_id}/assign-template/",
            data={"template_id": str(self.template2.id)},
            format="json",
            HTTP_X_DEV_USER_EMAIL=self.manager.email,
        )
        self.assertEqual(response.status_code, 404)

    def test_assign_template_template_not_found(self):
        """Verify 404 Not Found when template UUID does not exist or is invalid."""
        non_existent_template_id = uuid.uuid4()
        response = self.client.patch(
            f"/api/agents/{self.agent.id}/assign-template/",
            data={"template_id": str(non_existent_template_id)},
            format="json",
            HTTP_X_DEV_USER_EMAIL=self.manager.email,
        )
        self.assertEqual(response.status_code, 404)

        # Invalid UUID format string
        response_invalid = self.client.patch(
            f"/api/agents/{self.agent.id}/assign-template/",
            data={"template_id": "not-a-valid-uuid"},
            format="json",
            HTTP_X_DEV_USER_EMAIL=self.manager.email,
        )
        self.assertEqual(response_invalid.status_code, 404)

        # Non-primitive type like list
        response_type_err = self.client.patch(
            f"/api/agents/{self.agent.id}/assign-template/",
            data={"template_id": [1, 2, 3]},
            format="json",
            HTTP_X_DEV_USER_EMAIL=self.manager.email,
        )
        self.assertEqual(response_type_err.status_code, 404)
