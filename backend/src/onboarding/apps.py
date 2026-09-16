"""App configuration for src.onboarding."""

from django.apps import AppConfig


class OnboardingConfig(AppConfig):
    """Django app configuration for onboarding."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "src.onboarding"
    label = "onboarding"
    verbose_name = "Bienvenue Onboarding app"
