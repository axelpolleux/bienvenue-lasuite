"""Tests for Fichiers verification service and mock endpoints."""

import urllib.error
from unittest.mock import patch
from django.test import Client, TestCase, override_settings
from src.onboarding.services.suite_verifier import check_user_fichiers


class SuiteVerifierTest(TestCase):
    """Test suite for Fichiers verification service and mock."""

    def setUp(self):
        self.client = Client()

    def test_mock_fichiers_endpoint_success(self):
        """Verify local mock endpoint returns 200 by default."""
        response = self.client.get("/api/mock-suite/fichiers/users/alex.martin@gouv.fr/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["exists"])

    def test_mock_fichiers_endpoint_404_simulation(self):
        """Verify query param ?status=404 simulates unverified state."""
        response = self.client.get("/api/mock-suite/fichiers/users/unknown@gouv.fr/?status=404")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["exists"])

    @patch("src.onboarding.services.suite_verifier.urllib.request.urlopen")
    def test_check_user_fichiers_success(self, mock_urlopen):
        """Verify service returns True on HTTP 200."""
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.status = 200
        mock_response.getcode.return_value = 200

        exists, err = check_user_fichiers("alex.martin@gouv.fr")
        self.assertTrue(exists)
        self.assertIsNone(err)

    @patch("src.onboarding.services.suite_verifier.urllib.request.urlopen")
    def test_check_user_fichiers_http_404(self, mock_urlopen):
        """Verify service returns False and appropriate message on 404."""
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://mock-url",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None,
        )
        exists, err = check_user_fichiers("unknown@gouv.fr")
        self.assertFalse(exists)
        self.assertEqual(err, "User not found in Fichiers service.")

    @patch("src.onboarding.services.suite_verifier.urllib.request.urlopen")
    def test_check_user_fichiers_http_500(self, mock_urlopen):
        """Verify service returns False and error message on HTTP 500."""
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://mock-url",
            code=500,
            msg="Internal Server Error",
            hdrs={},
            fp=None,
        )
        exists, err = check_user_fichiers("alex.martin@gouv.fr")
        self.assertFalse(exists)
        self.assertIn("HTTP Error 500: Internal Server Error", err)

    @patch("src.onboarding.services.suite_verifier.urllib.request.urlopen")
    def test_check_user_fichiers_service_unreachable(self, mock_urlopen):
        """Verify service returns False and error message on connection error."""
        mock_urlopen.side_effect = urllib.error.URLError(reason="Connection refused")
        exists, err = check_user_fichiers("alex.martin@gouv.fr")
        self.assertFalse(exists)
        self.assertIn("Service unreachable: <urlopen error Connection refused>", err)

    @patch("src.onboarding.services.suite_verifier.urllib.request.urlopen")
    def test_check_user_fichiers_unexpected_status_code(self, mock_urlopen):
        """Verify service returns False when status code is not 200."""
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.getcode.return_value = 204

        exists, err = check_user_fichiers("alex.martin@gouv.fr")
        self.assertFalse(exists)
        self.assertEqual(err, "Unexpected status code: 204")

    @patch("src.onboarding.services.suite_verifier.urllib.request.urlopen")
    def test_check_user_fichiers_timeout(self, mock_urlopen):
        """Verify service returns False and error message on request timeout."""
        mock_urlopen.side_effect = TimeoutError("Request timed out")
        exists, err = check_user_fichiers("alex.martin@gouv.fr")
        self.assertFalse(exists)
        self.assertIn("Service unreachable: Request timed out", err)

    @override_settings(LA_SUITE_FICHIERS_TOKEN="secret-fichiers-token-123")
    @patch("src.onboarding.services.suite_verifier.urllib.request.urlopen")
    def test_check_user_fichiers_with_auth_token(self, mock_urlopen):
        """Verify Authorization Bearer header is attached when service token is set."""
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.getcode.return_value = 200

        exists, err = check_user_fichiers("alex.martin@gouv.fr")
        self.assertTrue(exists)
        self.assertIsNone(err)

        # Inspect the urllib.request.Request passed to urlopen
        called_req = mock_urlopen.call_args[0][0]
        self.assertEqual(
            called_req.get_header("Authorization"),
            "Bearer secret-fichiers-token-123",
        )
