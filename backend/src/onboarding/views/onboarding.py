"""API views for new agent onboarding workflow."""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from src.onboarding.models import AgentTodoStatus, TodoItem, ValidationTypeChoices
from src.onboarding.serializers import OnboardingBundleSerializer
from src.onboarding.services.suite_verifier import check_user_fichiers


class OnboardingMeView(APIView):
    """GET /api/onboarding/me/ returning full agent bundle."""

    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        """Retrieve onboarding profile, assigned template, checklist, and resources.

        Returns 200 with the full onboarding bundle, or 404 if no Agent profile is found.
        """
        agent = getattr(request, "agent", getattr(request.user, "agent", None))
        if not agent:
            return Response(
                {"error": "Agent profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OnboardingBundleSerializer(agent, context={"agent": agent})
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyTodoView(APIView):
    """POST /api/todos/{id}/verify/ verifying automated service check."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk) -> Response:
        """Verify account provisioning on external service (e.g. Fichiers) and complete task.

        Returns 200 with completion timestamp on success, 400 if verification fails,
        or 404 if the task is not found in the agent's assigned template.
        """
        agent = getattr(request, "agent", getattr(request.user, "agent", None))
        if not agent:
            return Response(
                {"error": "Agent profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not agent.assigned_template:
            return Response(
                {"error": "No assigned template."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        todo = get_object_or_404(agent.get_all_todos(), id=pk)

        # Automated check via service verifier
        exists, err_msg = check_user_fichiers(agent.email)
        if not exists:
            return Response(
                {
                    "todo_id": str(todo.id),
                    "done": False,
                    "error": err_msg or "Service verification failed.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        status_rec, _ = AgentTodoStatus.objects.get_or_create(
            agent=agent,
            todo_item=todo,
        )
        status_rec.done = True
        status_rec.done_at = timezone.now()
        status_rec.save(update_fields=["done", "done_at"])

        return Response(
            {
                "todo_id": str(todo.id),
                "done": True,
                "done_at": status_rec.done_at.isoformat(),
                "message": "Account verified successfully.",
            },
            status=status.HTTP_200_OK,
        )


class ToggleTodoView(APIView):
    """POST /api/todos/{id}/toggle/ for manual checklist items."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk) -> Response:
        """Toggle manual checklist item completion state.

        Accepts optional `done` boolean in request body (defaults to True).
        Returns 200 with updated status, 400 if no template is assigned,
        or 404 if the task is not found in the agent's assigned template.
        """
        agent = getattr(request, "agent", getattr(request.user, "agent", None))
        if not agent:
            return Response(
                {"error": "Agent profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not agent.assigned_template:
            return Response(
                {"error": "No assigned template."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        todo = get_object_or_404(agent.get_all_todos(), id=pk)
        done_val = request.data.get("done", True) if isinstance(request.data, dict) else True

        status_rec, _ = AgentTodoStatus.objects.get_or_create(
            agent=agent,
            todo_item=todo,
        )
        status_rec.done = bool(done_val)
        status_rec.done_at = timezone.now() if status_rec.done else None
        status_rec.save(update_fields=["done", "done_at"])

        return Response(
            {
                "todo_id": str(todo.id),
                "done": status_rec.done,
                "done_at": status_rec.done_at.isoformat() if status_rec.done_at else None,
            },
            status=status.HTTP_200_OK,
        )


class AcceptSignatureView(APIView):
    """POST /api/signature/accept/ to validate official email signature."""

    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        """Mark email signature as accepted for the authenticated agent.

        Returns 200 with confirmation message, or 404 if agent profile is missing.
        """
        agent = getattr(request, "agent", getattr(request.user, "agent", None))
        if not agent:
            return Response(
                {"error": "Agent profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        agent.signature_accepted = True
        agent.save(update_fields=["signature_accepted"])

        if agent.assigned_template:
            sig_todos = TodoItem.objects.filter(
                template=agent.assigned_template,
                validation_type=ValidationTypeChoices.SIGNATURE,
            )
            now = timezone.now()
            for sig_todo in sig_todos:
                AgentTodoStatus.objects.update_or_create(
                    agent=agent,
                    todo_item=sig_todo,
                    defaults={"done": True, "done_at": now},
                )

        return Response(
            {
                "signature_accepted": True,
                "message": "Signature validated successfully.",
            },
            status=status.HTTP_200_OK,
        )

