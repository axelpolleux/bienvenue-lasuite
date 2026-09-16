from urllib.parse import urlencode

from django.conf import settings


def provider_logout(request):
    """Build the Keycloak end-session URL so logout also ends the SSO session."""
    params = {
        "client_id": settings.OIDC_RP_CLIENT_ID,
        "post_logout_redirect_uri": request.build_absolute_uri(
            settings.LOGOUT_REDIRECT_URL
        ),
    }
    return f"{settings.OIDC_OP_LOGOUT_ENDPOINT}?{urlencode(params)}"
