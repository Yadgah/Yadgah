from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import News


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ["title", "content", "is_active"]


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")
    confirm_password = forms.CharField(
        widget=forms.PasswordInput, label="تکرار رمز عبور"
    )
    profile_picture = forms.ImageField(label="عکس پروفایل", required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("رمز عبور و تکرار آن یکسان نیستند!")

        return cleaned_data

    def persian_to_latin(self, text):
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

        # حذف فاصله‌های خالی اول و آخر متن
        leading_spaces = len(text) - len(text.lstrip(" "))
        trailing_spaces = len(text) - len(text.rstrip(" "))
        stripped_text = text.strip()

        # تبدیل کاراکترها
        converted = "".join(
            persian_to_english.get(char, char) for char in stripped_text
        )

        # بازگرداندن فاصله‌های خالی اول و آخر
        return " " * leading_spaces + converted + " " * trailing_spaces

    def save(self, commit=True):
        user = super().save(commit=False)

        # تبدیل نام و نام خانوادگی به لاتین برای تولید نام کاربری
        converted_first_name = self.persian_to_latin(self.cleaned_data["first_name"])
        converted_last_name = self.persian_to_latin(self.cleaned_data["last_name"])

        base_username = f"{converted_first_name}_{converted_last_name}"
        username = base_username
        counter = 1

        # اطمینان از یکتا بودن نام کاربری
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user.username = username
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()

        # ذخیره عکس پروفایل اگر وجود داشته باشد
        profile_picture = self.cleaned_data.get("profile_picture")
        if profile_picture:
            UserProfile.objects.create(user=user, profile_picture=profile_picture)
        else:
            UserProfile.objects.create(user=user)

        return user


# فرم ورود
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="نام کاربری", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        label="رمز عبور", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
