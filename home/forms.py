import random
import string

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import Label, Question, Reply, UserProfile


class SignUpForm(forms.ModelForm):
    """
    Form for user signup, generating a unique username if it already exists.
    """

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "helloworld"}
        ),
        label="Username",
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "example@domain.com"}
        ),
        label="Email",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "helloworld123123"}
        ),
        label="Password",
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean_username(self):
        """
        Ensure the username is unique or generate a new one if it already exists.
        """
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            new_username = self.generate_unique_username(username)
            return new_username
        return username

    def generate_unique_username(self, base_username):
        """
        Generate a unique username by appending random numbers/letters if needed.
        """
        while True:
            suffix = "".join(random.choices(string.digits, k=4))
            new_username = f"{base_username}_{suffix}"
            if not User.objects.filter(username=new_username).exists():
                return new_username


class LoginForm(AuthenticationForm):
    """
    Custom login form with styled fields.
    """

    username = forms.CharField(
        label="Username", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class UserForm(forms.ModelForm):
    """
    Form for updating user details like username and email.
    """

    class Meta:
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        # Add 'form-control' class to each field for consistent styling
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class UserProfileForm(forms.ModelForm):
    """
    Form for updating the user's profile details such as first name, last name, and avatar.
    """

    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name", "avatar", "show_email"]

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # Add 'form-control' class to each field for consistent styling
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class QuestionForm(forms.ModelForm):
    """
    Form for creating and editing a question, including label selection.
    """

    class Meta:
        model = Question
        fields = ["title", "content", "labels"]
        widgets = {
            "content": forms.Textarea(
                attrs={"placeholder": "سوال شما (Markdown پشتیبانی میشود.)", "rows": 5}
            ),
        }

    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "custom-multi-select"}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            # فقط برچسب‌های عمومی یا برچسب‌هایی که همین کاربر ساخته است.
            self.fields["labels"].queryset = Label.objects.filter(
                Q(is_custom=False) | Q(created_by=user)
            )


class ReplyForm(forms.ModelForm):
    """
    Form for creating a reply to a question.
    """

    class Meta:
        model = Reply
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"placeholder": "پاسخ شما (Markdown پشتیبانی میشود.)", "size": 2}
            ),
        }
        labels = {"content": ""}
