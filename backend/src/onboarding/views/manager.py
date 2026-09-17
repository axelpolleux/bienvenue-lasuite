"""API views for manager dashboard and agent administration."""

from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from src.onboarding.models import Agent, RoleChoices, Template
from src.onboarding.permissions import IsManager
from src.onboarding.serializers import ManagerAgentOverviewSerializer
from src.onboarding.services.grist_sync import sync_all

__all__ = ["ManagerOverviewView", "AssignTemplateView", "SyncGristView"]


class ManagerOverviewView(APIView):
    """GET /api/manager/overview/ returning newcomers list and total count."""

    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request) -> Response:
        """List all new agents with onboarding progress and current active step.

        Requires MANAGER role. Returns 200 with total_newcomers count and agents list.
        """
        newcomers = (
            Agent.objects.filter(role=RoleChoices.NEW_AGENT)
            .select_related("assigned_template")
            .order_by("-created_at")
        )
        serializer = ManagerAgentOverviewSerializer(newcomers, many=True)
        return Response(
            {
                "total_newcomers": newcomers.count(),
                "agents": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class AssignTemplateView(APIView):
    """PATCH /api/agents/<uuid:pk>/assign-template/ reassigning onboarding template."""

    permission_classes = [IsAuthenticated, IsManager]

    def patch(self, request, pk) -> Response:
        """Reassign an onboarding template to the specified agent.

        Requires MANAGER role. Expects `template_id` in request body.
        Returns 200 on success, 400 if template_id is missing, or 404 if agent or template not found.
        """
        template_id = (
            request.data.get("template_id")
            if isinstance(request.data, dict)
            else None
        )
        if not template_id or (isinstance(template_id, str) and not template_id.strip()):
            return Response(
                {"error": "template_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        agent = get_object_or_404(Agent, pk=pk)

        try:
            template = Template.objects.get(pk=template_id)
        except (Template.DoesNotExist, DjangoValidationError, ValueError, TypeError):
            return Response(
                {"error": "Template not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        agent.assigned_template = template
        agent.save(update_fields=["assigned_template"])

        return Response(
            {
                "agent_id": str(agent.id),
                "template_id": str(template.id),
                "template_name": template.name,
                "message": "Template assigned successfully.",
            },
            status=status.HTTP_200_OK,
        )


class SyncGristView(APIView):
    """POST /api/manager/sync-grist/ pulling every Grist table into Postgres.

    Triggered by the manager's "Save" button after editing templates in
    Grist — no webhook, the manager explicitly asks for a resync.
    """

    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request) -> Response:
        """Pull all 5 Grist tables and upsert by grist_row_id.

        Returns 200 with a per-table synced-row count, or 502 if Grist
        could not be reached.
        """
        try:
            results = sync_all()
        except Exception:
            return Response(
                {"error": "Could not reach Grist."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {"message": "Sync complete.", "synced": results},
            status=status.HTTP_200_OK,
        )
