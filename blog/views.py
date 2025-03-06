import os
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect, render
from PIL import Image

from .forms import PostForm
from .models import Post


def post_list(request):
    posts = Post.objects.filter(published=True).order_by("-created_at")
    return render(request, "blog/post_list.html", {"posts": posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, published=True)
    return render(request, "blog/post_detail.html", {"post": post})


@login_required
def post_create(request):
    if request.method == "POST":
        # توجه داشته باشید که request.FILES را نیز پاس می‌دهیم
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # اگر فایلی آپلود شده باشد (مثلاً تصویر):
            if post.image:
                # تصویر آپلودی را با Pillow باز می‌کنیم
                img = Image.open(post.image)

                # اطمینان پیدا می‌کنیم که حالت رنگی تصویر RGB باشد
                # (فرمت‌هایی مانند PNG ممکن است RGBA باشند و باید به RGB تبدیل شوند)
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # یک بافر موقتی در حافظه برای نگهداری داده‌های وب‌پی
                webp_io = BytesIO()

                # ذخیره تصویر در فرمت WebP در بافر
                img.save(webp_io, format="WEBP")

                # ساخت یک ContentFile از بافر
                webp_content = ContentFile(webp_io.getvalue())

                # تغییر پسوند فایل به .webp
                filename_without_ext, _ = os.path.splitext(post.image.name)
                webp_filename = f"{filename_without_ext}.webp"

                # جایگزینی فایل اصلی با فایل وب‌پی
                post.image.save(webp_filename, webp_content, save=False)

            # در نهایت پست را ذخیره می‌کنیم
            post.save()

            return redirect("post_list")
    else:
        form = PostForm()

    return render(request, "blog/post_create.html", {"form": form})
