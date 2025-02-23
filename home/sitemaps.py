from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import News, Question


class QuestionSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Question.objects.all().order_by("-created_at")  # Ensure ordering

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse("question_detail", args=[str(obj.id)])


class NewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return News.objects.filter(is_active=True).order_by(
            "-published_at"
        )  # Ensure ordering

    def lastmod(self, obj):
        return obj.published_at

    def location(self, obj):
        return reverse("news_list")


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return [
            "index",
            "privacy_policy",
            "mit_license",
            "rules",
            "leaderboard",
            "explore",
        ]

    def location(self, item):
        return reverse(item)
