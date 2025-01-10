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
        widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Confirm Password",
    )
    profile_picture = forms.ImageField(label="Profile Picture", required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password"]
        labels = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email",
            "password": "Password",
        }
        label_suffix = ""  # Remove default colon in field labels

    def clean_email(self):
        """
        Ensure the email is unique across all users.
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def persian_to_latin(self, text):
        """
        Convert Persian characters to Latin for use in usernames or slugs.
        """
        persian_to_english = {
            "ا": "a", "ب": "b", "پ": "p", "ت": "t", "ث": "s", "ج": "j", "چ": "ch",
            "ح": "h", "خ": "kh", "د": "d", "ذ": "z", "ر": "r", "ز": "z", "ژ": "zh",
            "س": "s", "ش": "sh", "ص": "s", "ض": "z", "ط": "t", "ظ": "z", "ع": "a",
            "غ": "gh", "ف": "f", "ق": "gh", "ک": "k", "گ": "g", "ل": "l", "م": "m",
            "ن": "n", "و": "v", "ه": "h", "ی": "y", " ": "_",
        }
        stripped_text = text.strip()
        return "".join(persian_to_english.get(char, char) for char in stripped_text)

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
        fields = ['username', 'email']
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        # Add 'form-control' class to each field for consistent styling
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class UserProfileForm(forms.ModelForm):
    """
    Form for updating the user's profile details such as first name, last name, and avatar.
    """
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'avatar']
    
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # Add 'form-control' class to each field for consistent styling
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class QuestionForm(forms.ModelForm):
    """
    Form for creating a question.
    """
    class Meta:
        model = Question
        fields = ['title', 'content']
        labels = {
            'title': 'Question Title',
            'content': 'Question Description',
        }

class ReplyForm(forms.ModelForm):
    """
    Form for creating a reply to a question.
    """
    class Meta:
        model = Reply
        fields = ['content']
