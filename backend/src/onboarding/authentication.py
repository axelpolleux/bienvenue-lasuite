"""Authentication classes for Bienvenue à La Suite BFF."""

from typing import Optional, Tuple
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from src.onboarding.models import Agent, RoleChoices, Template


class AuthenticatedAgentWrapper:
    """Wrapper presenting a Django user-like interface for an Agent."""

    def __init__(self, agent: Agent):
        self.agent = agent
        self.is_authenticated = True
        self.is_anonymous = False

    @property
    def id(self):
        return self.agent.id

    @property
    def pk(self):
        return self.agent.pk

    @property
    def email(self) -> str:
        return self.agent.email

    @property
    def role(self) -> str:
        return self.agent.role

    @property
    def is_manager(self) -> bool:
        return self.agent.role == RoleChoices.MANAGER

    def __getattr__(self, name: str):
        return getattr(self.agent, name)

    def __str__(self) -> str:
        return str(self.agent)


class DevOrKeycloakAuthentication(BaseAuthentication):
    """Authenticates via X-Dev-User-Email in DEBUG mode, or Bearer JWT in production."""

    def _authenticate_dev_user(
        self, request
    ) -> Optional[Tuple[AuthenticatedAgentWrapper, None]]:
        """Authenticate request via X-Dev-User-Email when DEBUG is True."""
        if not getattr(settings, "DEBUG", False):
            return None

        dev_email = request.META.get("HTTP_X_DEV_USER_EMAIL")
        if not dev_email or not dev_email.strip():
            return None

        email_clean = dev_email.strip().lower()
        agent, _ = Agent.objects.get_or_create(
            email=email_clean,
            defaults={
                "name": email_clean.split("@")[0].replace(".", " ").title(),
                "role": RoleChoices.NEW_AGENT,
            },
        )
        wrapper = AuthenticatedAgentWrapper(agent)
        request.agent = agent
        return (wrapper, None)

    def _authenticate_session_user(
        self, request
    ) -> Optional[Tuple[AuthenticatedAgentWrapper, None]]:
        """Authenticate request via Django session from OIDC SSO."""
        django_user = getattr(getattr(request, "_request", request), "user", None)
        if django_user is None:
            django_user = getattr(request, "user", None)

        if not django_user or not getattr(django_user, "is_authenticated", False):
            return None

        user_email = getattr(django_user, "email", None)
        if not user_email or not user_email.strip():
            return None

        email_clean = user_email.strip().lower()
        first = getattr(django_user, "first_name", "")
        last = getattr(django_user, "last_name", "")
        full_name = (
            f"{first} {last}".strip()
            or email_clean.split("@")[0].replace(".", " ").title()
        )
        agent, _ = Agent.objects.get_or_create(
            email=email_clean,
            defaults={
                "name": full_name,
                "role": RoleChoices.NEW_AGENT,
            },
        )
        if agent.assigned_template is None:
            agent.assigned_template = Template.objects.first()
            agent.save(update_fields=["assigned_template"])

        wrapper = AuthenticatedAgentWrapper(agent)
        request.agent = agent
        return (wrapper, None)

    def _authenticate_bearer_token(
        self, request
    ) -> Optional[Tuple[AuthenticatedAgentWrapper, None]]:
        """Authenticate request via Bearer token."""
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        parts = auth_header.split(maxsplit=1)
        token = parts[1].strip() if len(parts) > 1 else ""
        if getattr(settings, "DEBUG", False) and token == "test-token":
            agent = Agent.objects.filter(role=RoleChoices.NEW_AGENT).first()
            if agent:
                request.agent = agent
                return (AuthenticatedAgentWrapper(agent), None)
        raise AuthenticationFailed("Invalid or expired Keycloak token.")

    def authenticate(self, request) -> Optional[Tuple[AuthenticatedAgentWrapper, None]]:
        """Authenticate request via dev header, session cookie, or Bearer token."""
        dev_auth = self._authenticate_dev_user(request)
        if dev_auth:
            return dev_auth

        session_auth = self._authenticate_session_user(request)
        if session_auth:
            return session_auth

        return self._authenticate_bearer_token(request)

    def authenticate_header(self, request) -> str:
        """Return Bearer challenge to ensure unauthenticated requests yield 401 Unauthorized."""
        return 'Bearer realm="api"'
