# home/apps.py
from django.apps import AppConfig


class HomeConfig(AppConfig):
    name = "home"

    def ready(self):
        import home.signals  # به این ترتیب سیگنال‌ها بارگذاری می‌شوند
