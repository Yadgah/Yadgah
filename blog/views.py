import os
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect, render
from PIL import Image

from home.models import UserProfile

from .forms import PostForm
from .models import Post, PostSlugHistory


def post_list(request):
    posts = Post.objects.filter(published=True).order_by("-created_at")
    return render(request, "blog/post_list.html", {"posts": posts})


def post_detail(request, slug):
    try:
        post = Post.objects.get(slug=slug)
    except Post.DoesNotExist:
        slug_history = get_object_or_404(PostSlugHistory, slug=slug)
        post = slug_history.post
        return redirect("post_detail", slug=post.slug, permanent=True)
    return render(request, "blog/post_detail.html", {"post": post})


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
