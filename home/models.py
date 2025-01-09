import os

from django.contrib.auth.models import User
from django.db import models

class Question(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Reply(models.Model):
    question = models.ForeignKey(Question, related_name='replies', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Reply to {self.question.title} by {self.user.username}"
        
class UserProfile(models.Model):
    """
    Model representing a user's profile with an optional avatar.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    def __str__(self):
        return self.user.username


class News(models.Model):
    """
    Model representing a news article.
    """

    title = models.CharField(max_length=200, verbose_name="News Title")
    content = models.TextField(verbose_name="Content")
    published_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Published Date"
    )
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="news", verbose_name="Author"
    )

    def __str__(self):
        return self.title
