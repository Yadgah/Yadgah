import markdown
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Represents the profile of a user, linked to the Django User model.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    score = models.PositiveIntegerField(default=0)  # Store user score for ranking

    def __str__(self):
        return f"{self.user.username} Profile"

    def increase_score(self, amount=1):
        """Increase the score of the user safely."""
        self.score += amount
        self.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile for new users if it does not exist."""
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the user profile when the user is saved."""
    # Check if the user has a profile before trying to save it
    if hasattr(instance, "userprofile"):
        instance.userprofile.save()


class Label(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default="#000000")  # Hex color code
    is_custom = models.BooleanField(default=False)  # Identifies custom labels

    def __str__(self):
        return self.name


class Question(models.Model):
    """
    Represents a question posted by a user.
    """

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
    labels = models.ManyToManyField(Label, related_name="questions", blank=True)
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    @property
    def like_count(self):
        """Returns the number of likes for the question."""
        return self.likes_count.count()

    @property
    def trend_score(self):
        """
        A custom property to calculate a trend score based on likes and views.
        Higher score indicates the question is more "trendy".
        """
        # For example, the trend score can be based on likes and views.
        return self.like_count * 2 + self.view_count

    @classmethod
    def get_trending_questions(cls):
        """Returns questions sorted by trend score."""
        return cls.objects.all().order_by("-trend_score")[
            :10
        ]  # Returns top 10 trending question


class Reply(models.Model):
    """
    Represents a reply to a question, with Markdown content.
    """

    content = models.TextField()  # Stores the reply content in Markdown format
    question = models.ForeignKey(
        Question, related_name="replies", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.content[:50]

    def get_content_as_html(self):
        """
        Converts the Markdown content into HTML for display in the question view.
        """
        return markdown.markdown(self.content, extensions=["fenced_code"])


class QuestionReaction(models.Model):
    """
    Represents a reaction (like or dislike) to a question by a user.
    """

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
    Represents a news article.
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
