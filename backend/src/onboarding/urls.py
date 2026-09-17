"""URL configuration for src.onboarding endpoints."""

from django.urls import path
from src.onboarding.views.manager import (
    AssignTemplateView,
    ManagerOverviewView,
    SyncGristView,
)
from src.onboarding.views.mock_suite import mock_fichiers_user_view
from src.onboarding.views.onboarding import (
    AcceptSignatureView,
    OnboardingMeView,
    ToggleTodoView,
    VerifyTodoView,
)

urlpatterns = [
    # Agent onboarding endpoints
    path("onboarding/me/", OnboardingMeView.as_view(), name="onboarding-me"),
    path("todos/<uuid:pk>/verify/", VerifyTodoView.as_view(), name="todo-verify"),
    path("todos/<uuid:pk>/toggle/", ToggleTodoView.as_view(), name="todo-toggle"),
    path("signature/accept/", AcceptSignatureView.as_view(), name="signature-accept"),
    # Manager endpoints
    path("manager/overview/", ManagerOverviewView.as_view(), name="manager-overview"),
    path(
        "agents/<uuid:pk>/assign-template/",
        AssignTemplateView.as_view(),
        name="agent-assign-template",
    ),
    path(
        "manager/sync-grist/",
        SyncGristView.as_view(),
        name="manager-sync-grist",
    ),
    # Local mock testing endpoints
    path(
        "mock-suite/fichiers/users/<str:email>/",
        mock_fichiers_user_view,
        name="mock-fichiers-user",
    ),
]

