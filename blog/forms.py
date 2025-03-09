from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "body", "published", "image")
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "placeholder": "محتوای شما (Markdown پشتیبانی میشود.)",
                    "rows": 8,
                }
            ),
        }
