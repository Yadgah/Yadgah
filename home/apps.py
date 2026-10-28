from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"

    def ready(self):
        # NOTE: Do NOT query the database here. ready() runs on every
        # management command (including `migrate` on a fresh database),
        # before the tables exist -- see issue #167. Database defaults
        # (AI_Agent user, default labels) are created via the
        # `post_migrate` signal in home/signals.py instead.
        import home.signals  # noqa: F401
