import markdown
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


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
        """
        Increases the user's score by the specified amount.
        
        Args:
            amount (int): The amount by which to increase the score. Defaults to 1.
        """
        self.score += amount
        self.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Creates a UserProfile for new users if it does not already exist.
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Saves the user profile whenever the user is saved.
    """
    if hasattr(instance, "userprofile"):
        instance.userprofile.save()


class Label(models.Model):
    """
    Represents a label associated with a question (e.g., category or topic).
    """

    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default="#000000")  # Hex color code

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
    likes_count = models.ManyToManyField(User, related_name="liked_questions", blank=True)
    dislikes_count = models.ManyToManyField(User, related_name="disliked_questions", blank=True)
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
        Calculates a trend score based on likes and views.
        Higher score indicates the question is more "trendy".
        """
        return self.like_count * 2 + self.view_count

    @classmethod
    def search(cls, query):
        """
        Searches for questions based on a query string in the title or content.

        Args:
            query (str): The search term.

        Returns:
            QuerySet: A list of questions that match the query.
        """
        return cls.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    @classmethod
    def get_trending_questions(cls):
        """
        Retrieves the top 10 trending questions based on their trend score.

        Returns:
            QuerySet: A list of the top 10 trending questions.
        """
        return cls.objects.all().order_by("-trend_score")[:10]
    
    def get_absolute_url(self):
        return reverse("question_detail", args=[str(self.id)])


class Reply(models.Model):
    """
    Represents a reply to a question, with Markdown content.
    """

    content = models.TextField()  # Stores the reply content in Markdown format
    question = models.ForeignKey(Question, related_name="replies", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content[:50]

    def get_content_as_html(self):
        """
        Converts the Markdown content into HTML for display.
        
        Returns:
            str: The content rendered as HTML.
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

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="reactions")
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
    published_at = models.DateTimeField(auto_now_add=True, verbose_name="Published Date")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="news", verbose_name="Author")

    @classmethod
    def search(cls, query):
        """
        Searches for news articles based on a query string in the title or content.

        Args:
            query (str): The search term.

        Returns:
            QuerySet: A list of news articles that match the query.
        """
        return cls.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    def __str__(self):
        return self.title
