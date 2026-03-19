"""
Django app configuration for achievements system.
"""

from django.apps import AppConfig


class AchievementsConfig(AppConfig):
    """Configuration for the achievements Django app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'world.achievements'
    verbose_name = 'Achievement System'

    def ready(self):
        """Import signal handlers when app is ready."""
        pass