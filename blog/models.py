from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, allow_unicode=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts"
    )
    body = CKEditor5Field("Body", config_name="default")
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="posts/", null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.pk and self.title != Post.objects.get(pk=self.pk).title:
            old_slug = self.slug
            self.slug = slugify(self.title, allow_unicode=True)
            PostSlugHistory.objects.create(post=self, slug=old_slug)
        elif not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class PostSlugHistory(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="slug_history"
    )
    slug = models.SlugField(unique=True, allow_unicode=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.slug


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"
