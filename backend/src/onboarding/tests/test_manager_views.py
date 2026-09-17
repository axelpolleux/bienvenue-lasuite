"""Test suite for manager overview and template assignment endpoints."""

import uuid
import requests
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

    # -------------------------------------------------------------------------
    # POST /api/manager/sync-grist/pull/ and /push/
    # -------------------------------------------------------------------------

    def test_sync_grist_pull_unauthorized(self):
        """Verify 401 Unauthorized when no credentials provided for pull."""
        response = self.client.post("/api/manager/sync-grist/pull/")
        self.assertEqual(response.status_code, 401)

    def test_sync_grist_pull_forbidden_for_new_agent(self):
        """Verify 403 Forbidden when authenticated as a NEW_AGENT for pull."""
        response = self.client.post(
            "/api/manager/sync-grist/pull/",
            HTTP_X_DEV_USER_EMAIL=self.agent.email,
        )
        self.assertEqual(response.status_code, 403)

    def test_sync_grist_pull_success(self):
        """Verify 200 OK and synced count when manager triggers pull."""
        from unittest.mock import patch
        with patch("src.onboarding.views.manager.sync_all") as mock_sync:
            mock_sync.return_value = {"Members": 5, "TodoItems": 12}
            response = self.client.post(
                "/api/manager/sync-grist/pull/",
                HTTP_X_DEV_USER_EMAIL=self.manager.email,
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["message"], "Sync complete.")
            self.assertEqual(data["synced"]["Members"], 5)

    def test_sync_grist_pull_error_returns_502(self):
        """Verify 502 Bad Gateway when Grist cannot be reached during pull."""
        from unittest.mock import patch
        with patch("src.onboarding.views.manager.sync_all") as mock_sync:
            mock_sync.side_effect = requests.RequestException("Grist down")
            response = self.client.post(
                "/api/manager/sync-grist/pull/",
                HTTP_X_DEV_USER_EMAIL=self.manager.email,
            )
            self.assertEqual(response.status_code, 502)
            self.assertEqual(response.json(), {"error": "Could not reach Grist."})

    def test_sync_grist_pull_unexpected_error_returns_500(self):
        """Verify 500 Internal Server Error on unexpected exception during pull."""
        from unittest.mock import patch
        with patch("src.onboarding.views.manager.sync_all") as mock_sync:
            mock_sync.side_effect = RuntimeError("Database integrity failure")
            response = self.client.post(
                "/api/manager/sync-grist/pull/",
                HTTP_X_DEV_USER_EMAIL=self.manager.email,
            )
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json(), {"error": "Internal synchronization error."})

    def test_sync_grist_push_unauthorized(self):
        """Verify 401 Unauthorized when no credentials provided for push."""
        response = self.client.post("/api/manager/sync-grist/push/")
        self.assertEqual(response.status_code, 401)

    def test_sync_grist_push_forbidden_for_new_agent(self):
        """Verify 403 Forbidden when authenticated as a NEW_AGENT for push."""
        response = self.client.post(
            "/api/manager/sync-grist/push/",
            HTTP_X_DEV_USER_EMAIL=self.agent.email,
        )
        self.assertEqual(response.status_code, 403)

    def test_sync_grist_push_success(self):
        """Verify 200 OK when manager triggers push."""
        from unittest.mock import patch
        with patch("src.onboarding.views.manager.push_progress_to_grist") as mock_push:
            mock_push.return_value = {"updated": 3, "created": 1, "members_affected": 2}
            response = self.client.post(
                "/api/manager/sync-grist/push/",
                HTTP_X_DEV_USER_EMAIL=self.manager.email,
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["message"], "Push complete.")
            self.assertEqual(data["results"]["updated"], 3)
            self.assertEqual(data["results"]["members_affected"], 2)

    def test_sync_grist_push_error_returns_502(self):
        """Verify 502 Bad Gateway when Grist cannot be reached during push."""
        from unittest.mock import patch
        with patch("src.onboarding.views.manager.push_progress_to_grist") as mock_push:
            mock_push.side_effect = requests.RequestException("Grist down")
            response = self.client.post(
                "/api/manager/sync-grist/push/",
                HTTP_X_DEV_USER_EMAIL=self.manager.email,
            )
            self.assertEqual(response.status_code, 502)
            self.assertEqual(response.json(), {"error": "Could not reach Grist."})

    def test_sync_grist_push_unexpected_error_returns_500(self):
        """Verify 500 Internal Server Error on unexpected exception during push."""
        from unittest.mock import patch
        with patch("src.onboarding.views.manager.push_progress_to_grist") as mock_push:
            mock_push.side_effect = RuntimeError("Unexpected calculation error")
            response = self.client.post(
                "/api/manager/sync-grist/push/",
                HTTP_X_DEV_USER_EMAIL=self.manager.email,
            )
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json(), {"error": "Internal synchronization error."})

    # -------------------------------------------------------------------------
    # POST /api/manager/sync-grist/ (legacy alias)
    # -------------------------------------------------------------------------

    def test_legacy_sync_grist_unauthorized(self):
        """Verify 401 Unauthorized on legacy endpoint when unauthenticated."""
        response = self.client.post("/api/manager/sync-grist/")
        self.assertEqual(response.status_code, 401)

    def test_legacy_sync_grist_forbidden_for_new_agent(self):
        """Verify 403 Forbidden on legacy endpoint when authenticated as NEW_AGENT."""
        response = self.client.post(
            "/api/manager/sync-grist/",
            HTTP_X_DEV_USER_EMAIL=self.agent.email,
        )
        self.assertEqual(response.status_code, 403)

    def test_legacy_sync_grist_success(self):
        """Verify 200 OK and synced count on legacy endpoint when manager triggers sync."""
        from unittest.mock import patch
        with patch("src.onboarding.views.manager.sync_all") as mock_sync:
            mock_sync.return_value = {"Members": 4, "Templates": 2}
            response = self.client.post(
                "/api/manager/sync-grist/",
                HTTP_X_DEV_USER_EMAIL=self.manager.email,
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["message"], "Sync complete.")
            self.assertEqual(data["synced"]["Members"], 4)
            self.assertEqual(data["synced"]["Templates"], 2)

    def test_legacy_sync_grist_error_returns_502(self):
        """Verify 502 Bad Gateway on legacy endpoint when Grist is unreachable."""
        from unittest.mock import patch
        with patch("src.onboarding.views.manager.sync_all") as mock_sync:
            mock_sync.side_effect = requests.RequestException("Grist down")
            response = self.client.post(
                "/api/manager/sync-grist/",
                HTTP_X_DEV_USER_EMAIL=self.manager.email,
            )
            self.assertEqual(response.status_code, 502)
            self.assertEqual(response.json(), {"error": "Could not reach Grist."})

    def test_legacy_sync_grist_unexpected_error_returns_500(self):
        """Verify 500 Internal Server Error on legacy endpoint on unexpected failure."""
        from unittest.mock import patch
        with patch("src.onboarding.views.manager.sync_all") as mock_sync:
            mock_sync.side_effect = RuntimeError("Database deadlocked")
            response = self.client.post(
                "/api/manager/sync-grist/",
                HTTP_X_DEV_USER_EMAIL=self.manager.email,
            )
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json(), {"error": "Internal synchronization error."})
