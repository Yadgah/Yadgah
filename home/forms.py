import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import News, UserProfile, Question, Reply


class NewsForm(forms.ModelForm):
    """
    Form for creating and editing news articles.
    """

    class Meta:
        model = News
        fields = ["title", "content", "is_active"]


class SignUpForm(forms.ModelForm):
    """
    Form for user signup, including custom validations for email and password.
    """

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}), label="رمز عبور"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="تکرار رمز عبور",
    )
    profile_picture = forms.ImageField(label="عکس پروفایل", required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password"]
        labels = {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "email": "ایمیل",
            "password": "رمز عبور",
        }
        label_suffix = ""  # Remove default colon in field labels

    def clean_email(self):
        """
        Ensure the email is unique across all users.
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("این ایمیل قبلاً ثبت شده است.")
        return email

    def persian_to_latin(self, text):
        """
        Convert Persian characters to Latin for use in usernames or slugs.
        """
        persian_to_english = {
            "ا": "a",
            "ب": "b",
            "پ": "p",
            "ت": "t",
            "ث": "s",
            "ج": "j",
            "چ": "ch",
            "ح": "h",
            "خ": "kh",
            "د": "d",
            "ذ": "z",
            "ر": "r",
            "ز": "z",
            "ژ": "zh",
            "س": "s",
            "ش": "sh",
            "ص": "s",
            "ض": "z",
            "ط": "t",
            "ظ": "z",
            "ع": "a",
            "غ": "gh",
            "ف": "f",
            "ق": "gh",
            "ک": "k",
            "گ": "g",
            "ل": "l",
            "م": "m",
            "ن": "n",
            "و": "v",
            "ه": "h",
            "ی": "y",
            " ": "_",
        }
        stripped_text = text.strip()
        return "".join(persian_to_english.get(char, char) for char in stripped_text)


class LoginForm(AuthenticationForm):
    """
    Custom login form with styled fields.
    """

    username = forms.CharField(
        label="نام کاربری", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        label="رمز عبور", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class UserProfileForm(forms.ModelForm):
    """
    Form for updating the user's profile, specifically the avatar.
    """

    class Meta:
        model = UserProfile
        fields = ["avatar"]


class UserForm(forms.ModelForm):
    """
    Form for updating basic user details.
    """

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'content']  # عنوان و محتوای سوال
        labels = {
            'title': 'عنوان سوال',
            'content': 'توضیحات سوال',
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']
