import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (LoginForm, NewsForm, QuestionForm, ReplyForm, SignUpForm,
                    UserForm, UserProfileForm)
from .models import News, Question, UserProfile


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


# User signup view
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

            # Use default profile picture if none is provided by user
            if not request.FILES.get("profile_picture"):
                # Path to default profile picture
                user.profile_picture = "profile_picture.jpg"

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


# Home view to show recent questions and news
def home_view(request):
    # Get the most recent questions
    questions = Question.objects.all().order_by("-created_at")[:5]

    # Get the most recent active news
    news_items = News.objects.filter(is_active=True).order_by("-published_at")[:5]

    # Send data to the template
    return render(
        request, "index.html", {"questions": questions, "news_items": news_items}
    )


# View to list news
def news_list(request):
    news_items = News.objects.filter(is_active=True).order_by("-published_at")
    if not news_items:
        messages.warning(request, "No news available.")
    return render(request, "news/news_list.html", {"news_items": news_items})


# View to ask a question
@login_required
def ask_question(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.user = (
                request.user
            )  # Set the logged-in user as the question author
            question.save()
            messages.success(request, "Your question has been submitted successfully.")
            return redirect("index")  # Redirect to the home page
    else:
        form = QuestionForm()

    return render(request, "ask_question.html", {"form": form})


# View for question detail and replies
def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    # Handling reply submission
    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.question = question
            reply.user = request.user
            reply.save()
            return redirect("question_detail", question_id=question.id)
    else:
        form = ReplyForm()

    return render(request, "question_detail.html", {"question": question, "form": form})


# View for user's profile and their questions
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    questions = user.questions.all()  # Get questions asked by the user
    return render(
        request, "user_profile.html", {"profile_user": user, "questions": questions}
    )


# View to load questions for pagination
def load_questions(request):
    page = request.GET.get("page", 1)  # Get page number (default is 1)
    page = int(page)  # Convert page number to integer

    # Load questions and use Paginator for pagination
    questions = Question.objects.all().order_by("-created_at")
    paginator = Paginator(questions, 5)  # 5 questions per page

    try:
        questions_page = paginator.page(page)
    except EmptyPage:
        return HttpResponse("")  # Return empty response if page is out of range

    return render(request, "partials/question_list.html", {"questions": questions_page})


# View to delete user profile
@login_required
def delete_profile(request):
    user_profile = request.user.userprofile
    user_profile.delete()  # Delete user profile
    request.user.delete()  # Delete user account
    messages.success(request, "Your profile has been successfully deleted.")
    return redirect("home")  # Redirect to home or any other page


import json

# views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Question, QuestionReaction


@csrf_exempt
def toggle_reaction(request, question_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "کاربر باید وارد حساب کاربری خود شود"}, status=401
        )

    question = get_object_or_404(Question, id=question_id)
    data = json.loads(request.body)
    reaction_type = data.get("reaction_type")

    # Check if the reaction is either 'like' or 'dislike'
    if reaction_type not in ["like", "dislike"]:
        return JsonResponse({"error": "واکنش معتبر نیست"}, status=400)

    # Get or create the reaction
    reaction_type_value = (
        QuestionReaction.LIKE if reaction_type == "like" else QuestionReaction.DISLIKE
    )
    reaction, created = QuestionReaction.objects.get_or_create(
        question=question,
        user=request.user,
        defaults={"reaction_type": reaction_type_value},
    )

    if not created:
        # If the reaction exists, toggle the reaction type
        if reaction.reaction_type == reaction_type_value:
            reaction.delete()  # Remove the reaction if it's the same
        else:
            reaction.reaction_type = reaction_type_value
            reaction.save()

    # Count the reactions
    likes_count = QuestionReaction.objects.filter(
        question=question, reaction_type=QuestionReaction.LIKE
    ).count()
    dislikes_count = QuestionReaction.objects.filter(
        question=question, reaction_type=QuestionReaction.DISLIKE
    ).count()

    return JsonResponse({"likes": likes_count, "dislikes": dislikes_count})


# views.py
from django.shortcuts import get_object_or_404, render

from .forms import ReplyForm
from .models import Question, QuestionReaction


def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    # تعداد لایک‌ها و دیس‌لایک‌ها را محاسبه می‌کنیم
    likes_count = QuestionReaction.objects.filter(
        question=question, reaction_type=QuestionReaction.LIKE
    ).count()
    dislikes_count = QuestionReaction.objects.filter(
        question=question, reaction_type=QuestionReaction.DISLIKE
    ).count()

    # فرض کنید که فرم ارسال پاسخ دارید
    form = ReplyForm(request.POST or None)

    if form.is_valid():
        # منطق ذخیره پاسخ
        form.save()

    return render(
        request,
        "question_detail.html",
        {
            "question": question,
            "form": form,
            "likes_count": likes_count,
            "dislikes_count": dislikes_count,
        },
    )
