import json
import os
import re
from datetime import timedelta
from io import BytesIO

import jdatetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.paginator import EmptyPage, Paginator
from django.db import models
from django.db.models import Count, ExpressionWrapper, F, FloatField, Q
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from blog.models import Post

from .ai import get_ai_reply
from .forms import (
    LoginForm,
    QuestionForm,
    ReplyForm,
    SignUpForm,
    UserForm,
    UserProfileForm,
)
from .models import Label, Question, QuestionReaction, Reply, Slide, UserProfile


# Helper function to process and validate POST request with success messages
def process_post_request(form, request, success_url, success_message=None):
    if form.is_valid():
        form.save()
        if success_message:
            messages.success(request, success_message)
        return redirect(success_url)
    return form


# Helper function to convert Gregorian to Jalali
def convert_to_jalali(date):
    if date:
        jalali_date = jdatetime.date.fromgregorian(date=date)
        return f"{jalali_date.day} {jalali_date.j_months_fa[jalali_date.month - 1]}"
    return ""


# Helper function to validate user data for registration and login
def validate_user_data(username, password, confirm_password, email):
    if not username or not password or not email:
        return "Username, email, and password are required."

    if password != confirm_password:
        return "Passwords do not match."

    if User.objects.filter(username=username).exists():
        return "Username already taken."

    return None


# Helper function to process form and handle validation errors
def process_form(form, request, redirect_url, success_message=None):
    if form.is_valid():
        form.save()
        if success_message:
            messages.success(request, success_message)
        return redirect(redirect_url)
    else:
        return render(request, "ask_question.html", {"form": form})


# Home view to show recent questions and news
def home_view(request):
    questions = Question.objects.all().order_by("-created_at")
    paginator = Paginator(questions, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Handling Ajax requests
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        questions_data = [
            {
                "id": question.id,
                "title": question.title,
                "content": question.content,
                "created_at": convert_to_jalali(question.created_at),
                "labels": [
                    {"name": label.name, "color": label.color}
                    for label in question.labels.all()
                ],
                "url": question.get_absolute_url(),
            }
            for question in page_obj
        ]
        return JsonResponse(
            {
                "questions": questions_data,
                "has_next": page_obj.has_next(),
            }
        )

    # Clean up expired slides
    Slide.objects.filter(expires_at__lt=timezone.now()).delete()
    slides = Slide.objects.all()

    # Aggregate data for stats
    total_questions = Question.objects.count()
    total_replies = Reply.objects.count()
    total_users = User.objects.count()

    # Get top question of the week
    one_week_ago = timezone.now() - timedelta(days=7)
    top_question_of_week = (
        Question.objects.filter(created_at__gte=one_week_ago)
        .annotate(
            num_likes=Count("likes_count"),
            num_replies=Count("replies"),
            calculated_trend_score=ExpressionWrapper(
                (F("num_likes") * 2) + (F("num_replies") * 1) + (F("view_count") * 0.5),
                output_field=FloatField(),
            ),
        )
        .order_by("-calculated_trend_score")
        .first()
    )

    labels = Label.objects.filter(is_custom=False)

    return render(
        request,
        "index.html",
        {
            "questions": page_obj,
            "slides": slides,
            "show_load_more": questions.count() > 5,
            "total_questions": total_questions,
            "total_replies": total_replies,
            "total_users": total_users,
            "top_question_of_week": top_question_of_week,
            "labels": labels,
        },
    )


# User signup view with password validation
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        password = request.POST.get("password")

        # Password complexity check
        password_complexity = r"^(?=.*[a-zA-Z])(?=.*\d).{8,}$"
        if not re.fullmatch(password_complexity, password):
            messages.error(
                request,
                "Password must include at least one letter, one digit, and be at least 8 characters long.",
            )
            return render(request, "signup.html", {"form": form})

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(password)
            if not request.FILES.get("profile_picture"):
                user.profile_picture = "profile_picture.jpg"
            user.save()
            login(request, user)
            return redirect("index")

    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


# User login view
def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("index")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


# User logout view
def logout_view(request):
    logout(request)
    return redirect("index")


# User profile view with image processing
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
            profile_instance = profile_form.save(commit=False)

            # Handle image conversion to WebP format
            if profile_instance.avatar:
                try:
                    img = Image.open(profile_instance.avatar)
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    webp_io = BytesIO()
                    img.save(webp_io, format="WEBP")
                    webp_content = ContentFile(webp_io.getvalue())
                    webp_filename = (
                        f"{os.path.splitext(profile_instance.avatar.name)[0]}.webp"
                    )
                    profile_instance.avatar.save(
                        webp_filename, webp_content, save=False
                    )
                except Exception as e:
                    print(f"Error converting image to WebP: {e}")

            profile_instance.save()
            return redirect("profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)

    return render(
        request,
        "profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
        },
    )


# View to ask a question
@login_required
def ask_question(request):
    if request.method == "POST":
        form = QuestionForm(request.POST, user=request.user)
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user
            question.save()
            form.save_m2m()

            ai_reply_content = get_ai_reply(question.content)  # ارسال فقط content به AI
            ai_user, _ = User.objects.get_or_create(
                username="AI_Agent", defaults={"is_active": False}
            )

            Reply.objects.create(
                content=ai_reply_content,
                question=question,
                user=ai_user,
            )

            return redirect("question_detail", question_id=question.id)
    else:
        form = QuestionForm(user=request.user)

    return render(request, "ask_question.html", {"form": form})


# Create label view with enhanced error handling
def create_label(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name", "").strip()
            color = data.get("color", "#000000").strip()

            if not name:
                return JsonResponse({"error": "Label name is required."}, status=400)

            label, created = Label.objects.get_or_create(
                name=name,
                created_by=request.user,  # مهم! برای هر کاربر جداگانه
                defaults={"color": color, "is_custom": True},
            )

            if not created:
                return JsonResponse(
                    {"error": "Label already exists for this user."}, status=400
                )

            return JsonResponse(
                {
                    "message": "Label created successfully.",
                    "label": {"name": label.name, "color": label.color},
                },
                status=201,
            )
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Detail view for a specific question
def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    # Check if the user has already viewed the question in this session
    if not request.session.get(f"viewed_question_{question.id}", False):
        question.view_count += 1
        question.save()
        request.session[f"viewed_question_{question.id}"] = True

    likes_count = question.likes_count.count()
    dislikes_count = question.dislikes_count.count()

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

    # Convert Markdown content to HTML for rendering
    content_as_html = mark_safe(
        markdown.markdown(question.content, extensions=["fenced_code"])
    )

    # Handle the reply form
    form = ReplyForm(request.POST or None)
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
            "form": form,
            "view_count": question.view_count,
        },
    )


# View to delete a reply with permission checks
@login_required
def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)

    # Ensure only the reply owner or admin can delete it
    if reply.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden()

    # Deleting the reply
    question_id = reply.question.id
    reply.delete()
    return redirect("question_detail", question_id=question_id)


# View to delete a question
@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if question.user == request.user:
        question.delete()
        messages.success(request, "سوال با موفقیت حذف شد.")
    else:
        messages.error(request, "شما دسترسی پاک کردن ندارید.")

    return redirect("index")


# View for user profiles displaying their questions
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(UserProfile, user=user)
    questions = Question.objects.filter(user=user)
    published_posts = Post.objects.filter(author=user, published=True)
    unpublished_posts = (
        Post.objects.filter(author=user, published=False)
        if request.user.is_authenticated
        else []
    )

    context = {
        "profile_user": user,
        "user_profile": user_profile,
        "questions": questions,
        "published_posts": published_posts,
        "unpublished_posts": unpublished_posts,
    }

    return render(request, "user_profile.html", context)


# View to delete user profile
@login_required
def delete_profile(request):
    user_profile = request.user.userprofile
    user_profile.delete()  # Delete user profile
    request.user.delete()  # Delete user account
    messages.success(request, "Your profile has been successfully deleted.")
    return redirect("index")


# View to toggle like/dislike reactions on questions
@csrf_exempt
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

    if reply.question.user == request.user:
        reply.is_approved = True
        reply.save()

        if reply.user != reply.question.user:
            user_profile = reply.question.user.userprofile
            user_profile.score += 10  # Assuming 10 points for approval
            user_profile.save()

    return redirect("question_detail", question_id=reply.question.id)


# Privacy Policy view
def privacy_policy(request):
    return render(request, "privacy_policy.html")


# Rules page view
def rules(request):
    return render(request, "rules.html")


# Leaderboard view for ranking users by score
def leaderboard(request):
    users = UserProfile.objects.all().order_by("-score")
    return render(request, "leaderboard.html", {"users": users})


# Explore view to display trending questions
def explore(request):
    trending_questions = Question.objects.annotate(
        num_likes=Count("likes_count"),
        num_replies=Count("replies"),
        calculated_trend_score=ExpressionWrapper(
            (F("num_likes") * 2) + (F("num_replies") * 1) + (F("view_count") * 0.5),
            output_field=FloatField(),
        ),
    ).order_by("-calculated_trend_score")[:10]

    return render(request, "explore.html", {"trending_questions": trending_questions})


# Search view for questions
def search_view(request):
    query = request.GET.get("q", "")
    questions = Question.search(query) if query else Question.objects.none()

    return render(
        request, "search_results.html", {"query": query, "questions": questions}
    )


# Robots.txt file view
def robots_txt(request):
    domain = request.get_host()
    content = f"""User-agent: *
Disallow: /admin/
Disallow: /login/
Disallow: /signup/
# Disallow: /profile/
Disallow: /delete_profile/
Allow: /
Sitemap: https://{domain}/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")


# Custom 404 Error Page
def custom_page_not_found(request, exception):
    return render(request, "404.html", status=404)


# Custom 500 Error Page
def custom_error(request):
    return render(request, "500.html", status=500)


# Edit Question view
@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.user != question.user and not request.user.is_staff:
        return HttpResponseForbidden(
            "You do not have permission to edit this question."
        )

    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect("question_detail", question_id=question.id)
    else:
        form = QuestionForm(instance=question)

    return render(request, "edit_question.html", {"form": form, "question": question})


# View to edit a reply
@login_required
def edit_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)

    if request.user != reply.user and not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to edit this reply.")

    if request.method == "POST":
        form = ReplyForm(request.POST, instance=reply)
        if form.is_valid():
            form.save()
            return redirect("question_detail", question_id=reply.question.id)
    else:
        form = ReplyForm(instance=reply)

    return render(request, "edit_reply.html", {"form": form, "reply": reply})


# API to handle user signup
@api_view(["POST"])
def signup_api(request):
    username = request.data.get("username")
    password = request.data.get("password")
    confirm_password = request.data.get("confirm_password")
    email = request.data.get("email")

    error_message = validate_user_data(username, password, confirm_password, email)
    if error_message:
        return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    return Response(
        {"message": f"User {user.username} registered successfully."},
        status=status.HTTP_201_CREATED,
    )


# API to handle user login
@api_view(["POST"])
def login_api(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is not None:
        tokens = get_tokens_for_user(user)
        return Response(
            {"message": "Login successful.", "tokens": tokens},
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
        )


# Donate view
def donate(request):
    return render(request, "donate.html")


# Slide detail view with dynamic template selection based on slide type
def slide_detail(request, slug):
    slide = get_object_or_404(Slide, slug=slug)

    template_map = {
        "course": "slides/detail_course.html",
        "competition": "slides/detail_competition.html",
        "news": "slides/detail_news.html",
    }

    template_name = template_map.get(slide.type, "slides/detail.html")
    return render(request, template_name, {"slide": slide})


# Filter questions based on label ID
def filter_questions(request):
    label_id = request.GET.get("label_id")
    if label_id:
        questions = Question.objects.filter(labels__id=label_id).order_by("-created_at")
    else:
        questions = Question.objects.all().order_by("-created_at")

    html = render_to_string("partials/question_list.html", {"questions": questions})
    return JsonResponse({"html": html})
