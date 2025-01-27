from django.apps import AppConfig


class HomeConfig(AppConfig):
    name = "home"

    def ready(self):
        import home.signals  # This will load the signals # noqa: F401
