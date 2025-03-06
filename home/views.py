import json
import re
from PIL import Image
from io import BytesIO
import os
from django.core.files.base import ContentFile
import jdatetime
import markdown
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, Paginator
from django.db import models
from django.db.models import Count, F, FloatField, Q
from django.db.models.expressions import ExpressionWrapper
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

from blog.models import Post  # برای دسترسی به پست‌ها

from .forms import (
    LoginForm,
    NewsForm,
    QuestionForm,
    ReplyForm,
    SignUpForm,
    UserForm,
    UserProfileForm,
)
from .models import Label, News, Question, QuestionReaction, Reply, UserProfile


# Decorator to restrict access to staff members only
def staff_member_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)


# Home view to show recent questions and news
def home_view(request):
    questions = Question.objects.all().order_by("-created_at")
    paginator = Paginator(questions, 5)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    def convert_to_jalali(date):
        if date:
            jalali_date = jdatetime.date.fromgregorian(date=date)
            return f"{jalali_date.day} {jalali_date.j_months_fa[jalali_date.month - 1]}"
        return ""

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        questions_data = [
            {
                "id": question.id,
                "title": question.title,
                "content": question.content,
                "created_at": convert_to_jalali(
                    question.created_at
                ),  # تبدیل به تاریخ شمسی
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

    news_items = News.objects.filter(is_active=True).order_by("-published_at")[:5]
    return render(
        request,
        "index.html",
        {
            "questions": page_obj,
            "news_items": news_items,
            "show_load_more": questions.count() > 5,
        },
    )


# User signup view
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        password = request.POST.get("password")
        request.POST.get("confirm_password")

        # Validate password and confirm password
        # if password != confirm_password:
        #     messages.error(request, "Passwords do not match.")
        #     return render(request, "signup.html", {"form": form})

        # Password complexity check: At least one letter and one number
        password_complexity = r"^(?=.*[a-zA-Z])(?=.*\d).{8,}$"
        if not re.fullmatch(password_complexity, password):
            messages.error(
                request,
                "Password must include at least one letter, one digit, and be at least 8 characters long.",
            )
            return render(request, "signup.html", {"form": form})

        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data.get("username")
            user.set_password(password)
            user.first_name = ""  # Leave first name empty
            user.last_name = ""  # Leave last name empty

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
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()

            profile_instance = profile_form.save(commit=False)

            if profile_instance.avatar:
                try:
                    img = Image.open(profile_instance.avatar)

                    if img.mode != 'RGB':
                        img = img.convert('RGB')

                    webp_io = BytesIO()
                    img.save(webp_io, format='WEBP')  # quality=80

                    webp_content = ContentFile(webp_io.getvalue())

                    filename_without_ext, _ = os.path.splitext(profile_instance.avatar.name)
                    webp_filename = f"{filename_without_ext}.webp"

                    profile_instance.avatar.save(webp_filename, webp_content, save=False)
                except Exception as e:
                    print(f"Error converting image to WebP: {e}")

            profile_instance.save()

            messages.success(request, "Profile updated successfully.")
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
        form = QuestionForm(request.POST, user=request.user)  # اینجا user را پاس می‌دهیم
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user
            question.save()
            form.save_m2m()  # ذخیره رابطه‌ی many-to-many برچسب‌ها
            messages.success(request, "Your question has been submitted successfully.")
            return redirect("question_detail", question_id=question.id)
    else:
        form = QuestionForm(user=request.user)  # اینجا هم user را پاس می‌دهیم

    return render(request, "ask_question.html", {"form": form})


def create_label(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name", "").strip()
            color = data.get("color", "#000000").strip()

            if not name:
                return JsonResponse({"error": "Label name is required."}, status=400)

            # بررسی اینکه آیا برای همین کاربر، برچسبی با این نام وجود دارد یا خیر
            label, created = Label.objects.get_or_create(
                name=name,
                created_by=request.user,  # مهم!
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
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method."}, status=405)


def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    # Check if the user has already viewed the question in this session
    if not request.session.get(f"viewed_question_{question.id}", False):
        # Increment the view count
        question.view_count += 1
        question.save()

        # Mark that the user has viewed the question in this session
        request.session[f"viewed_question_{question.id}"] = True

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
            "view_count": question.view_count,  # Pass view count to the template
        },
    )


@csrf_exempt
def edit_reply(request, reply_id):
    if request.method == "POST":
        reply = get_object_or_404(Reply, id=reply_id)
        reply.content = request.POST.get("content")
        reply.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


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

    # Check if the current user is the author of the question
    if question.user == request.user:
        question.delete()
        messages.success(request, "سوال با موفقیت حذف شد.")
    else:
        messages.error(request, "شما دسترسی پاک کردن ندارید.")

    return redirect("index")  # Redirect to home or any o:ther page


# View for user profiles displaying their questions
def user_profile(request, username):
    # 1. واکشی کاربر با توجه به username
    user = get_object_or_404(User, username=username)

    # 2. واکشی پروفایل کاربر
    user_profile = get_object_or_404(UserProfile, user=user)

    # 3. واکشی سؤالات پرسیده‌شده توسط این کاربر
    questions = Question.objects.filter(user=user)

    # 4. واکشی پست‌های منتشرشده و منتشرنشده کاربر
    published_posts = Post.objects.filter(author=user, published=True)
    unpublished_posts = Post.objects.filter(author=user, published=False)

    # 5. رندر تمپلیت به همراه کانتکست مورد نیاز
    context = {
        "profile_user": user,
        "user_profile": user_profile,  # اضافه کردن پروفایل کاربر به کانتکست
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
        # تایید پاسخ
        reply.is_approved = True
        reply.save()

        # به روزرسانی امتیاز کاربر (صاحب سوال)
        user_profile = reply.question.user.userprofile
        user_profile.score += 10  # فرض بر اینکه 10 امتیاز داده می‌شود
        user_profile.save()

    return redirect("question_detail", question_id=reply.question.id)


def privacy_policy(request):
    return render(request, "privacy_policy.html")


def mit_license(request):
    return render(request, "mit_license.html")


def rules(request):
    return render(request, "rules.html")


def leaderboard(request):
    # Get all users, order them by score (descending)
    users = UserProfile.objects.all().order_by("-score")  # Order by score
    return render(request, "leaderboard.html", {"users": users})


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


def search_view(request):
    query = request.GET.get("q", "")
    questions = Question.search(query) if query else Question.objects.none()
    news = News.search(query) if query else News.objects.none()

    return render(
        request,
        "search_results.html",
        {"query": query, "questions": questions, "news": news},
    )


def robots_txt(request):
    domain = request.get_host()  # Automatically get the domain name
    content = f"""User-agent: *
Disallow: /admin/
Disallow: /login/
Disallow: /signup/
# Disallow: /profile/
Disallow: /delete_profile/
Allow: /
Sitemap: https://{domain}/sitemap.xml
# dadmehr control google robots :>
"""
    return HttpResponse(content, content_type="text/plain")


def custom_page_not_found(request, exception):
    return render(request, "404.html", status=404)


def custom_error(request):
    return render(request, "500.html", status=500)
