"""Webhook receiver for Grist row-change notifications."""

import hmac
import json
import logging

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from src.onboarding.services.grist_sync import SYNCABLE_TABLES, sync_table

logger = logging.getLogger(__name__)


class GristWebhookView(APIView):
    """POST /api/webhooks/grist/ — Grist notifies a table changed, we pull and upsert it.

    The table to sync is read from the `table` query param (set per-webhook
    in Grist's Document Settings), falling back to a `tableId` field in the
    JSON body if present.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        configured_secret = settings.GRIST_WEBHOOK_SECRET
        provided_secret = request.query_params.get("secret") or request.META.get(
            "HTTP_X_GRIST_WEBHOOK_TOKEN", ""
        )
        if not configured_secret or not hmac.compare_digest(
            configured_secret, provided_secret or ""
        ):
            return Response(
                {"error": "Invalid or missing webhook secret."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        table_name = request.query_params.get("table")
        if not table_name:
            try:
                body = json.loads(request.body or b"{}")
            except json.JSONDecodeError:
                body = {}
            table_name = body.get("tableId")

        if table_name not in SYNCABLE_TABLES:
            return Response(
                {"error": f"Unknown or missing table. Expected one of {SYNCABLE_TABLES}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            synced_count = sync_table(table_name)
        except Exception:
            logger.exception("grist_sync failed for table %s", table_name)
            return Response(
                {"error": "Sync failed."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {"table": table_name, "synced": synced_count},
            status=status.HTTP_200_OK,
        )
