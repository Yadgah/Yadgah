from django.contrib.sitemaps import Sitemap
from django.urls import reverse_lazy
from .models import Question, News


class QuestionSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Question.objects.all()

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, "updated_at") else obj.created_at

    def location(self, obj):
        return reverse_lazy("question_detail", args=[obj.id])


class NewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def get_queryset(self):
        return News.objects.filter(is_active=True)

    def items(self):
        return self.get_queryset()

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, "updated_at") else obj.published_at

    def location(self, obj):
        return reverse_lazy("news_list")


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    static_pages = [
        "index",
        "privacy_policy",
        "mit_license",
        "rules",
        "leaderboard",
        "explore",
    ]

    def items(self):
        return self.static_pages

    def location(self, item):
        return reverse_lazy(item)
