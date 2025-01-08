from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import UserProfile, News
import re



class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ["title", "content", "is_active"]

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="تکرار رمز عبور")
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
        label_suffix = ""  # حذف دو نقطه در لیبل‌ها

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("این ایمیل قبلاً ثبت شده است.")
        return email

    def persian_to_latin(self, text):
        persian_to_english = {
            "ا": "a", "ب": "b", "پ": "p", "ت": "t", "ث": "s", "ج": "j", "چ": "ch",
            "ح": "h", "خ": "kh", "د": "d", "ذ": "z", "ر": "r", "ز": "z", "ژ": "zh",
            "س": "s", "ش": "sh", "ص": "s", "ض": "z", "ط": "t", "ظ": "z", "ع": "a",
            "غ": "gh", "ف": "f", "ق": "gh", "ک": "k", "گ": "g", "ل": "l", "م": "m",
            "ن": "n", "و": "v", "ه": "h", "ی": "y", " ": "_",
        }

        stripped_text = text.strip()
        converted = "".join(persian_to_english.get(char, char) for char in stripped_text)

        return converted

# فرم ورود
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="نام کاربری", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        label="رمز عبور", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']  # تغییر به 'avatar' به جای 'profile_picture'



class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']