import os
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from PIL import Image

from home.models import UserProfile

from .forms import CommentForm, PostForm
from .models import Comment, Post, PostSlugHistory


def post_list(request):
    posts = Post.objects.filter(published=True).order_by("-created_at")
    return render(request, "blog/post_list.html", {"posts": posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    # Only count a view once per session
    if not request.session.get(f"viewed_post_{post.id}", False):
        post.view_count += 1
        post.save(update_fields=["view_count"])
        request.session[f"viewed_post_{post.id}"] = True

    # Handling comment form submission
    if request.method == "POST" and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            # Create a new comment and associate it with the post and user
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect(
                "post_detail", slug=post.slug
            )  # Redirect to avoid re-posting on refresh
    else:
        comment_form = CommentForm()

    comments = post.comments.all()  # Fetch all comments for the post

    return render(
        request,
        "blog/post_detail.html",
        {"post": post, "comment_form": comment_form, "comments": comments},
    )


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # Handle image conversion to WebP format if provided
            if "image" in request.FILES:
                uploaded_file = request.FILES["image"]
                try:
                    img = Image.open(uploaded_file)
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    webp_io = BytesIO()
                    img.save(webp_io, format="WEBP")
                    webp_content = ContentFile(webp_io.getvalue())

                    filename_without_ext, _ = os.path.splitext(uploaded_file.name)
                    webp_filename = f"{filename_without_ext}.webp"

                    post.image.save(webp_filename, webp_content, save=False)
                except Exception as e:
                    print(f"Error converting image to WebP: {e}")

            post.save()

            # Increase score if the post is published
            if post.published:
                user_profile = UserProfile.objects.get(user=request.user)
                user_profile.increase_score(10)

            return redirect("post_list")
    else:
        form = PostForm()

    return render(request, "blog/post_create.html", {"form": form})


@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)

            # پردازش تصویر و تبدیل به WebP (در صورت ارسال)
            if "image" in request.FILES:
                uploaded_file = request.FILES["image"]
                try:
                    img = Image.open(uploaded_file)
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    webp_io = BytesIO()
                    img.save(webp_io, format="WEBP")
                    webp_content = ContentFile(webp_io.getvalue())

                    filename_without_ext, _ = os.path.splitext(uploaded_file.name)
                    webp_filename = f"{filename_without_ext}.webp"

                    post.image.save(webp_filename, webp_content, save=False)
                except Exception as e:
                    print(f"Error converting image to WebP: {e}")

            # اگر وضعیت پست از "پیش‌نویس" به "منتشر شده" تغییر کرده باشد، امتیاز کاربر را افزایش بده
            if post.published and not post.pk:  # بررسی اولین بار انتشار
                user_profile = UserProfile.objects.get(user=request.user)
                user_profile.increase_score(10)

            post.save()
            return redirect("post_detail", slug=post.slug)
    else:
        form = PostForm(instance=post)

    return render(request, "blog/post_edit.html", {"form": form, "post": post})


@login_required
@require_POST
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    post.delete()
    return redirect("post_list")


def short_link_redirect_by_id(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return redirect("post_detail", slug=post.slug)