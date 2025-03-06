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
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # اگر کاربر فایل تصویر آپلود کرده باشد
            if "image" in request.FILES:
                uploaded_file = request.FILES["image"]
                try:
                    img = Image.open(uploaded_file)
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    webp_io = BytesIO()
                    img.save(webp_io, format="WEBP")
                    webp_content = ContentFile(webp_io.getvalue())

                    # تغییر پسوند فایل به .webp
                    filename_without_ext, _ = os.path.splitext(uploaded_file.name)
                    webp_filename = f"{filename_without_ext}.webp"

                    # ذخیره فایل WebP به جای فایل اصلی
                    post.image.save(webp_filename, webp_content, save=False)
                except Exception as e:
                    print(f"Error converting image to WebP: {e}")

            post.save()
            return redirect("post_list")
    else:
        form = PostForm()

    return render(request, "blog/post_create.html", {"form": form})
