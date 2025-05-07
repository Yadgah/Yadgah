from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Post

from .models import Question


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Post.objects.all().order_by("-created_at")  # Ensure ordering

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse("post_detail", args=[str(obj.slug)])


class QuestionSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Question.objects.all().order_by("-created_at")  # Ensure ordering

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse("question_detail", args=[str(obj.id)])


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return [
            "index",
            "leaderboard",
            "explore",
            "post_list",
        ]

    def location(self, item):
        return reverse(item)
