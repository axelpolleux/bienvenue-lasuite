"""Custom permission classes for onboarding views."""

from rest_framework.permissions import BasePermission
from src.onboarding.models import RoleChoices


class IsManager(BasePermission):
    """Allows access only to authenticated managers."""

    def has_permission(self, request, view) -> bool:
        """Verify that the user is authenticated and holds the MANAGER role."""
        user = getattr(request, "user", None)
        if not (user and user.is_authenticated):
            return False

        agent = getattr(request, "agent", getattr(user, "agent", None))
        if agent is not None:
            return agent.role == RoleChoices.MANAGER

        if hasattr(user, "role"):
            return user.role == RoleChoices.MANAGER

        return False
