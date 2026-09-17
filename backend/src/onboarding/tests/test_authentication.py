from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory, override_settings
from rest_framework.exceptions import AuthenticationFailed
from src.onboarding.models import Agent, RoleChoices, Template
from src.onboarding.authentication import (
    DevOrKeycloakAuthentication,
    AuthenticatedAgentWrapper,
)


@override_settings(DEBUG=True)
class DevOrKeycloakAuthenticationTest(TestCase):
    """Test suite for development header and production authentication."""

    def setUp(self):
        self.factory = RequestFactory()
        self.auth = DevOrKeycloakAuthentication()
        self.agent = Agent.objects.create(
            email="alex.martin@gouv.fr",
            name="Alex Martin",
            role=RoleChoices.NEW_AGENT,
        )

    def test_auth_with_dev_header_when_debug_true(self):
        """Verify X-Dev-User-Email authenticates existing agent in debug mode."""
        request = self.factory.get("/", HTTP_X_DEV_USER_EMAIL="alex.martin@gouv.fr")
        user_auth = self.auth.authenticate(request)
        self.assertIsNotNone(user_auth)
        user, auth_token = user_auth
        self.assertEqual(user.agent.email, "alex.martin@gouv.fr")
        self.assertEqual(request.agent, self.agent)
        self.assertTrue(user.is_authenticated)
        self.assertFalse(user.is_anonymous)
        self.assertFalse(user.is_manager)
        self.assertEqual(user.id, self.agent.id)
        self.assertEqual(user.pk, self.agent.pk)

    def test_auth_with_nonexistent_dev_email_creates_agent(self):
        """Verify unknown email in dev mode auto-provisions agent for smooth DX."""
        request = self.factory.get("/", HTTP_X_DEV_USER_EMAIL="newbie@gouv.fr")
        user_auth = self.auth.authenticate(request)
        self.assertIsNotNone(user_auth)
        user, _ = user_auth
        self.assertEqual(user.agent.email, "newbie@gouv.fr")
        self.assertTrue(Agent.objects.filter(email="newbie@gouv.fr").exists())
        provisioned = Agent.objects.get(email="newbie@gouv.fr")
        self.assertEqual(provisioned.name, "Newbie")
        self.assertEqual(provisioned.role, RoleChoices.NEW_AGENT)
        self.assertEqual(request.agent, provisioned)

    def test_auth_with_whitespace_dev_header_returns_none(self):
        """Verify whitespace-only X-Dev-User-Email is ignored."""
        request = self.factory.get("/", HTTP_X_DEV_USER_EMAIL="   ")
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    def test_auth_with_dev_header_when_debug_false(self):
        """Verify X-Dev-User-Email is ignored when DEBUG is False."""
        with override_settings(DEBUG=False):
            request = self.factory.get("/", HTTP_X_DEV_USER_EMAIL="alex.martin@gouv.fr")
            result = self.auth.authenticate(request)
            self.assertIsNone(result)

    def test_auth_fails_when_no_header_and_no_token(self):
        """Verify request returns None when no auth credentials provided."""
        request = self.factory.get("/")
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    def test_auth_with_test_bearer_token_in_debug(self):
        """Verify Bearer test-token works in debug mode, even with extra whitespace."""
        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer    test-token   ")
        user_auth = self.auth.authenticate(request)
        self.assertIsNotNone(user_auth)
        user, token = user_auth
        self.assertEqual(user.agent.email, self.agent.email)
        self.assertEqual(request.agent, self.agent)

    def test_auth_with_invalid_bearer_token(self):
        """Verify invalid Bearer token raises AuthenticationFailed."""
        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer invalid-token")
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_authenticated_agent_wrapper(self):
        """Verify AuthenticatedAgentWrapper properties and delegation."""
        manager = Agent.objects.create(
            email="manager@gouv.fr",
            name="Super Manager",
            role=RoleChoices.MANAGER,
        )
        wrapper = AuthenticatedAgentWrapper(manager)
        self.assertTrue(wrapper.is_authenticated)
        self.assertFalse(wrapper.is_anonymous)
        self.assertTrue(wrapper.is_manager)
        self.assertEqual(wrapper.id, manager.id)
        self.assertEqual(wrapper.pk, manager.pk)
        self.assertEqual(wrapper.email, "manager@gouv.fr")
        self.assertEqual(wrapper.name, "Super Manager")  # via __getattr__
        self.assertEqual(wrapper.role, RoleChoices.MANAGER)
        self.assertEqual(str(wrapper), str(manager))

    def test_auth_with_session_user_existing_agent(self):
        """Verify session authentication works for existing agent."""
        user = User.objects.create_user(username="alex", email="alex.martin@gouv.fr")
        request = self.factory.get("/")
        request.user = user
        user_auth = self.auth.authenticate(request)
        self.assertIsNotNone(user_auth)
        wrapper, token = user_auth
        self.assertEqual(wrapper.agent.email, "alex.martin@gouv.fr")
        self.assertEqual(request.agent, self.agent)

    def test_auth_with_session_user_auto_provisions_and_assigns_template(self):
        """Verify session authentication auto-provisions agent and assigns default template."""
        template = Template.objects.create(
            name="Default Onboarding",
            grist_row_id="tpl-default-1",
        )
        user = User.objects.create_user(
            username="new.sso",
            email="new.sso@gouv.fr",
            first_name="Jean",
            last_name="Dupont",
        )
        request = self.factory.get("/")
        request.user = user
        user_auth = self.auth.authenticate(request)
        self.assertIsNotNone(user_auth)
        wrapper, token = user_auth
        self.assertEqual(wrapper.agent.email, "new.sso@gouv.fr")
        self.assertEqual(wrapper.agent.name, "Jean Dupont")
        self.assertEqual(wrapper.agent.assigned_template, template)
        self.assertEqual(request.agent, wrapper.agent)

    def test_auth_with_anonymous_session_user_returns_none(self):
        """Verify AnonymousUser on session does not authenticate."""
        request = self.factory.get("/")
        request.user = AnonymousUser()
        result = self.auth.authenticate(request)
        self.assertIsNone(result)
