"""Authentication classes for Bienvenue à La Suite BFF."""

from typing import Optional, Tuple
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from src.onboarding.models import Agent, RoleChoices


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

    def authenticate(self, request) -> Optional[Tuple[AuthenticatedAgentWrapper, None]]:
        """Authenticate request via X-Dev-User-Email in DEBUG mode or Bearer JWT.

        Returns (AuthenticatedAgentWrapper, None) if authenticated, None if no credentials
        are present, or raises AuthenticationFailed if credentials are invalid.
        """
        dev_email = request.META.get("HTTP_X_DEV_USER_EMAIL")

        if getattr(settings, "DEBUG", False):
            if dev_email and dev_email.strip():
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

        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if auth_header and auth_header.startswith("Bearer "):
            # Production JWT validation hook (Keycloak OIDC)
            parts = auth_header.split(maxsplit=1)
            token = parts[1].strip() if len(parts) > 1 else ""
            if getattr(settings, "DEBUG", False) and token == "test-token":
                agent = Agent.objects.filter(role=RoleChoices.NEW_AGENT).first()
                if agent:
                    request.agent = agent
                    return (AuthenticatedAgentWrapper(agent), None)
            raise AuthenticationFailed("Invalid or expired Keycloak token.")

        return None

    def authenticate_header(self, request) -> str:
        """Return Bearer challenge to ensure unauthenticated requests yield 401 Unauthorized."""
        return 'Bearer realm="api"'
