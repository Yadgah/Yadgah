import markdown
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.safestring import mark_safe


class UserProfile(models.Model):
    """
    Represents the profile of a user, linked to the Django User model.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    score = models.PositiveIntegerField(default=0)  # Store user score for ranking
    show_email = models.BooleanField(
        default=False, verbose_name="نمایش ایمیل به دیگران"
    )

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

    def ready(self):
        import myapp.signals


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

    name = models.CharField(max_length=100)  # دیگر unique=True نباشد
    color = models.CharField(max_length=7, default="#000000")
    is_custom = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="labels"
    )

    def __str__(self):
        return self.name

    class Meta:
        # جلو گیری از تعریف چند برچسب همنام توسط یک کاربر
        unique_together = ("name", "created_by")


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
    question = models.ForeignKey(
        Question, related_name="replies", on_delete=models.CASCADE
    )
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
        # استفاده از extensions کامل برای پشتیبانی از لیست‌ها، کد، خطوط جدید و...
        extensions = [
            'extra',           # برای جداول، فوتر و...
            'fenced_code',     # برای کدهای بلاک
            'tables',          # برای جداول
            'nl2br',           # برای تبدیل خطوط جدید به <br>
            'sane_lists',      # برای لیست‌های منطقی
        ]
        
        html_content = markdown.markdown(self.content, extensions=extensions)
        return mark_safe(html_content)


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


class Slide(models.Model):
    SLIDE_TYPES = (
        ("course", "دوره آموزشی"),
        ("competition", "مسابقه"),
        ("news", "خبر"),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    button_text = models.CharField(max_length=50, default="مشاهده")
    slug = models.SlugField(unique=True, blank=True)
    thumbnail = models.ImageField(upload_to="slides/", null=True, blank=True)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(editable=False)

    type = models.CharField(max_length=20, choices=SLIDE_TYPES, default="news")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان انقضا")

    class Meta:
        ordering = ["order"]

    def save(self, *args, **kwargs):
        if not self.pk:
            last_order = Slide.objects.aggregate(models.Max("order"))["order__max"] or 0
            self.order = last_order + 1

        if not self.slug:
            # ایجاد slug عددی بر اساس ترتیب ساخت
            base_id = Slide.objects.aggregate(models.Max("id"))["id__max"] or 0
            self.slug = str(base_id + 1)

        super().save(*args, **kwargs)

    def is_expired(self):
        return self.expires_at and self.expires_at <= timezone.now()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("slide_detail", kwargs={"slug": self.slug})
