import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"

    def ready(self):
        import home.signals  # noqa: F401

        try:
            from django.contrib.auth.models import User  # ایمپورت داخل متد

            User.objects.get_or_create(
                username="AI_Agent",
                defaults={
                    "is_active": False,
                    "email": "ai@yadgahh.com",
                    "first_name": "AI",
                    "last_name": "Agent",
                },
            )
            logger.info("AI_Agent user is ready.")
        except Exception as e:
            logger.error(f"Error creating AI_Agent user: {e}")
