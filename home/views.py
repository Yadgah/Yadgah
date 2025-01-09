import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, NewsForm, SignUpForm, UserForm, UserProfileForm, QuestionForm, ReplyForm
from .models import News, UserProfile, Question


# Decorator to restrict access to staff members only
def staff_member_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)


# View to create news (staff only)
@staff_member_required
def create_news(request):
    if request.method == "POST":
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user  # Set the current user as the author
            news.save()
            return redirect("news_list")  # Redirect to the news list after creation
    else:
        form = NewsForm()
    return render(request, "news/create_news.html", {"form": form})


# View to edit news (staff only)
@staff_member_required
def edit_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.method == "POST":
        form = NewsForm(request.POST, instance=news)
        if form.is_valid():
            form.save()
            return redirect("news_list")  # Redirect to the news list after editing
    else:
        form = NewsForm(instance=news)
    return render(request, "news/edit_news.html", {"form": form, "news": news})


# View for user signup
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validate password and confirm password
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "signup.html", {"form": form})

        # Password complexity check
        password_complexity = (
            r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]).{8,}$'
        )
        if not re.fullmatch(password_complexity, password):
            messages.error(
                request,
                "Password must include an uppercase letter, a digit, and a special character.",
            )
            return render(request, "signup.html", {"form": form})

        # Ensure unique username
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")
        base_username = f"{''.join(filter(str.isalnum, first_name))}_{''.join(filter(str.isalnum, last_name))}"
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        if form.is_valid():
            user = form.save(commit=False)
            user.username = username
            user.set_password(password)
            user.save()
            login(request, user)
            messages.success(request, "Signup successful!")
            return redirect("index")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


# View for user login
def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("index")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


# View for user logout
def logout_view(request):
    logout(request)
    return redirect("index")


# View for user profile
@login_required
def profile_view(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=user_profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)

    return render(
        request, "profile.html", {"user_form": user_form, "profile_form": profile_form}
    )


# View for searching (example, logic needs implementation)
def search_view(request):
    query = request.GET.get("q", "")
    return render(request, "search_results.html", {"query": query})


def home_view(request):
    # دریافت سوالات اخیر
    questions = Question.objects.all().order_by('-created_at')[:5]
    
    # دریافت اخبار جدید
    news_items = News.objects.filter(is_active=True).order_by('-published_at')[:5]
    
    # ارسال داده‌ها به قالب
    return render(request, 'index.html', {'questions': questions, 'news_items': news_items})

# View to list news
def news_list(request):
    news_items = News.objects.filter(is_active=True).order_by("-published_at")
    if not news_items:
        messages.warning(request, "No news available.")
    return render(request, "news/news_list.html", {"news_items": news_items})

@login_required
def ask_question(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user  # کاربر وارد شده را به عنوان نویسنده سوال تنظیم می‌کنیم
            question.save()
            messages.success(request, 'سوال شما با موفقیت ثبت شد.')
            return redirect('index')  # به صفحه اصلی هدایت می‌شود
    else:
        form = QuestionForm()

    return render(request, 'ask_question.html', {'form': form})

def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    # بررسی ارسال پاسخ
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.question = question
            reply.user = request.user
            reply.save()
            return redirect('question_detail', question_id=question.id)
    else:
        form = ReplyForm()

    return render(request, 'question_detail.html', {'question': question, 'form': form})