from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "body", "published", "image")
        widgets = {
            "body": CKEditor5Widget(config_name="default"),
        }
