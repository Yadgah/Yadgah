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
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    likes_count = models.ManyToManyField(
        User, related_name="liked_questions", blank=True
    )
    dislikes_count = models.ManyToManyField(
        User, related_name="disliked_questions", blank=True
    )

    # def likes_count(self):
    #     return self.likes.count()

    # def dislikes_count(self):
    #     return self.dislikes.count()

    def __str__(self):
        return self.title


class Reply(models.Model):
    # فیلدهای دیگر
    content = models.TextField()
    question = models.ForeignKey(
        "Question", related_name="replies", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # اضافه کردن فیلد is_approved
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.content[:50]


# from .models import Question


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
