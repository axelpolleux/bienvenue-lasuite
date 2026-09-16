"""Service module to verify agent accounts on La Suite services."""

import urllib.error
import urllib.parse
import urllib.request
from typing import Optional, Tuple
from django.conf import settings


def check_user_fichiers(email: str) -> Tuple[bool, Optional[str]]:
    """Query Fichiers (Nextcloud) user lookup API to verify account existence.

    Args:
        email: The institutional email address to verify.

    Returns:
        A tuple of (exists: bool, error_message: Optional[str]).
        If exists is True, error_message is None. If False, error_message
        contains the failure reason.

    Constraints:
        Enforces strict URL-encoding on email and a 5.0-second network timeout.
        Attaches Bearer token from settings.LA_SUITE_FICHIERS_TOKEN if configured.
    """
    encoded_email = urllib.parse.quote(email, safe="")
    base_url = getattr(
        settings,
        "LA_SUITE_FICHIERS_URL",
        "http://127.0.0.1:8000/api/mock-suite/fichiers/users/{email}/",
    )
    url = base_url.replace("{email}", encoded_email)

    headers = {
        "User-Agent": "Bienvenue-LaSuite/1.0",
        "Accept": "application/json",
        "OCS-APIREQUEST": "true",
    }
    service_token = getattr(settings, "LA_SUITE_FICHIERS_TOKEN", None)
    if service_token:
        headers["Authorization"] = f"Bearer {service_token}"

    req = urllib.request.Request(
        url,
        headers=headers,
    )

    try:
        with urllib.request.urlopen(req, timeout=5.0) as response:
            if response.getcode() == 200:
                return True, None
            return False, f"Unexpected status code: {response.getcode()}"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, "User not found in Fichiers service."
        return False, f"HTTP Error {e.code}: {e.reason}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return False, f"Service unreachable: {str(e)}"
