from urllib.parse import urlencode

from django.conf import settings


def provider_logout(request):
    """Build the Keycloak end-session URL so logout also ends the SSO session.

    Keycloak 18+ requires an id_token_hint (not just client_id) to end the
    session silently — without it, it shows a re-login confirmation screen
    instead of just logging out.
    """
    params = {
        "post_logout_redirect_uri": request.build_absolute_uri(
            settings.LOGOUT_REDIRECT_URL
        ),
    }
    id_token = request.session.get("oidc_id_token")
    if id_token:
        params["id_token_hint"] = id_token
    else:
        params["client_id"] = settings.OIDC_RP_CLIENT_ID
    return f"{settings.OIDC_OP_LOGOUT_ENDPOINT}?{urlencode(params)}"
