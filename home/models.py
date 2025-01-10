from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")

    def __str__(self):
        return self.title


class Reply(models.Model):
    question = models.ForeignKey(
        Question, related_name="replies", on_delete=models.CASCADE
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="replies")

    def __str__(self):
        return f"Reply to {self.question.title} by {self.user.username}"


from django.contrib.auth.models import User
# models.py
from django.db import models

from .models import Question


class QuestionReaction(models.Model):
    LIKE = 1
    DISLIKE = -1
    REACTION_CHOICES = [
        (LIKE, "Like"),
        (DISLIKE, "Dislike"),
    ]

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="reactions"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.IntegerField(choices=REACTION_CHOICES)

    class Meta:
        unique_together = ("question", "user")

    def __str__(self):
        return f"{self.user.username} {self.get_reaction_type_display()} {self.question.title}"


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
