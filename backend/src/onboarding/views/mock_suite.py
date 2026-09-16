"""Local mock endpoints simulating La Suite services for development and testing."""

from django.http import JsonResponse


def mock_fichiers_user_view(request, email: str) -> JsonResponse:
    """Simulate Fichiers (Nextcloud) user existence endpoint for testing and local dev.

    Accepts ?status=404 query parameter to simulate an unprovisioned user state.
    """
    status_param = request.GET.get("status")

    if status_param == "404":
        return JsonResponse(
            {
                "exists": False,
                "email": email,
                "message": "User not found in local mock Fichiers service.",
            },
            status=404,
        )

    return JsonResponse(
        {
            "exists": True,
            "email": email,
            "service": "Fichiers / Nextcloud",
            "message": "User active and storage initialized.",
        },
        status=200,
    )
