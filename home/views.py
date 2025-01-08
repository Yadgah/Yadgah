from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from .forms import UserProfileForm, LoginForm, NewsForm, SignUpForm, UserForm
from .models import News, UserProfile
import re
from django.contrib.auth.models import User


def staff_member_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)

@staff_member_required
def create_news(request):
    if request.method == "POST":
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user  # تعیین نویسنده به کاربر جاری
            news.save()
            return redirect("news_list")  # پس از ایجاد خبر، به صفحه لیست اخبار بروید
    else:
        form = NewsForm()
    return render(request, "news/create_news.html", {"form": form})

@staff_member_required
def edit_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.method == "POST":
        form = NewsForm(request.POST, instance=news)
        if form.is_valid():
            form.save()
            return redirect("news_list")  # پس از ویرایش، به صفحه لیست اخبار بروید
    else:
        form = NewsForm(instance=news)
    return render(request, "news/edit_news.html", {"form": form, "news": news})

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)  # ارسال فایل‌ها در درخواست
        
        # دریافت مقادیر رمز عبور و تکرار رمز عبور
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
        # بررسی تطابق رمز عبور و تکرار آن
        if password != confirm_password:
            messages.error(request, "رمز عبور و تکرار آن باید یکسان باشند.")
            return render(request, "signup.html", {"form": form})

        # شرایط پیچیدگی رمز عبور
        password_complexity = r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]).{8,}$'
        
        if not re.fullmatch(password_complexity, password):
            messages.error(request, "رمز عبور باید حداقل شامل یک حرف بزرگ، یک عدد و یک کاراکتر خاص باشد.")
            return render(request, "signup.html", {"form": form})

        # بررسی یکتایی نام کاربری
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        # تبدیل نام‌ها به لاتین برای ایجاد نام کاربری
        converted_first_name = ''.join([char for char in first_name if char.isalnum()])
        converted_last_name = ''.join([char for char in last_name if char.isalnum()])
        base_username = f"{converted_first_name}_{converted_last_name}"
        username = base_username
        counter = 1
        
        # اطمینان از یکتایی نام کاربری
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        if form.is_valid():  # فرم باید قبل از دسترسی به cleaned_data اعتبارسنجی شود
            # پس از اعتبارسنجی فرم، تغییرات را در cleaned_data اعمال می‌کنیم
            user = form.save(commit=False)
            user.username = username  # اختصاص نام کاربری یکتا به کاربر
            user.set_password(password)  # تنظیم رمز عبور
            user.save()  # ذخیره کاربر

            login(request, user)  # ورود خودکار پس از ثبت‌نام
            messages.success(request, "ثبت‌نام موفقیت‌آمیز بود!")
            return redirect("index")  # به صفحه اصلی هدایت شوید
        else:
            # اگر فرم معتبر نباشد، خطاهای فرم را به کاربر نمایش می‌دهیم
            messages.error(request, "لطفاً اطلاعات را به درستی وارد کنید.")
            for field in form.errors:
                messages.error(request, f"{field}: {form.errors[field][0]}")
    else:
        form = SignUpForm()

    return render(request, "signup.html", {"form": form})



# ویوی ورود
def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "ورود موفقیت‌آمیز بود!")
            return redirect("index")
        else:
            messages.error(request, "نام کاربری یا رمز عبور اشتباه است.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("/")

@login_required
def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)  # توجه کنید که request.FILES در اینجا مهم است
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'اطلاعات پروفایل شما با موفقیت بروزرسانی شد.')
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

def search_view(request):
    query = request.GET.get("q", "")
    # Perform the search logic here
    return render(request, "search_results.html", {"query": query})

def home_view(request):
    return render(request, 'index.html')

def news_list(request):
    news_items = News.objects.filter(is_active=True).order_by("-published_at")
    if not news_items:
        messages.warning(request, "هیچ خبری برای نمایش وجود ندارد.")
    return render(request, "news/news_list.html", {"news_items": news_items})
