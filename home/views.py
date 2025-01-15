import json
import re

import markdown
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, Paginator
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseRedirect, JsonResponse)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

from .forms import (LoginForm, NewsForm, QuestionForm, ReplyForm, SignUpForm,
                    UserForm, UserProfileForm)
from .models import News, Question, QuestionReaction, Reply, UserProfile, Label

# Decorator to restrict access to staff members only
def staff_member_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)


# View to create news (accessible by staff only)
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


# View to edit news (accessible by staff only)
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

            # Use default profile picture if none is provided by the user
            if not request.FILES.get("profile_picture"):
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
# Home view to show recent questions and news
def home_view(request):
    # Get the most recent questions with their labels
    questions = Question.objects.prefetch_related('labels').all().order_by("-created_at")[:5]
    # Get the most recent active news
    news_items = News.objects.filter(is_active=True).order_by("-published_at")[:5]

    print(questions[0].labels.all())  # چاپ لیبل‌های سوال اول


    # Send data to the template
    return render(
        request, "index.html", {
            "questions": questions,
            "news_items": news_items
        }
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
            # Add labels (if any) after saving the question
            form.save_m2m()  # Save many-to-many relationships (labels)
            return redirect('question_detail', question_id=question.id)
    else:
        form = QuestionForm()

    return render(request, "ask_question.html", {"form": form})


# View to display question details and handle likes/dislikes
def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    # Count likes and dislikes
    likes_count = question.likes_count.count()
    dislikes_count = question.dislikes_count.count()

    # Check if the user has liked or disliked this question
    user_liked = (
        request.user in question.likes_count.all()
        if request.user.is_authenticated
        else False
    )
    user_disliked = (
        request.user in question.dislikes_count.all()
        if request.user.is_authenticated
        else False
    )

    # Convert Markdown content to HTML
    content_as_html = mark_safe(
        markdown.markdown(question.content, extensions=["fenced_code"])
    )

    # Handle the reply form
    form = ReplyForm()
    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.question = question
            reply.save()
            return redirect("question_detail", question_id=question.id)

    return render(
        request,
        "question_detail.html",
        {
            "question": question,
            "content_as_html": content_as_html,
            "likes_count": likes_count,
            "dislikes_count": dislikes_count,
            "user_liked": user_liked,
            "user_disliked": user_disliked,
            "form": form,  # Pass the form to the template
        },
    )


# View for user profiles displaying their questions
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


@csrf_exempt  # Temporarily for testing; should not be used in production
def toggle_reaction(request, question_id):
    if request.method == "POST":
        try:
            question = get_object_or_404(Question, id=question_id)
            data = json.loads(request.body)
            reaction_type = data.get("reaction_type")

            if reaction_type == "like":
                if request.user in question.likes_count.all():
                    question.likes_count.remove(request.user)
                else:
                    question.likes_count.add(request.user)
                    question.dislikes_count.remove(request.user)
            elif reaction_type == "dislike":
                if request.user in question.dislikes_count.all():
                    question.dislikes_count.remove(request.user)
                else:
                    question.dislikes_count.add(request.user)
                    question.likes_count.remove(request.user)
            else:
                return JsonResponse({"error": "Invalid reaction type"}, status=400)

            return JsonResponse(
                {
                    "likes": question.likes_count.count(),
                    "dislikes": question.dislikes_count.count(),
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# View to approve a reply
@login_required
def approve_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    # Ensure only the owner of the question can approve
    if reply.question.user == request.user:
        reply.is_approved = True
        reply.save()
    return redirect("question_detail", question_id=reply.question.id)
