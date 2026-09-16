from django.apps import apps
from django.test import TestCase


class OnboardingConfigTest(TestCase):
    """Test onboarding app configuration."""

    def test_app_is_registered(self):
        """Verify src.onboarding is registered in Django installed apps."""
        app_config = apps.get_app_config("onboarding")
        self.assertEqual(app_config.name, "src.onboarding")
