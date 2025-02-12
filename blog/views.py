from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from .models import BlogPost
from .forms import BlogPostForm

def blog_list(request):
    posts = BlogPost.objects.all().order_by("-created_at")
    return render(request, "blog/blog_list.html", {"posts": posts})

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    return render(request, "blog/blog_detail.html", {"post": post})

@login_required
def create_blog_post(request):
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.save()
            messages.success(request, "مقاله با موفقیت ایجاد شد.")
            return redirect(reverse("blog_detail", kwargs={"slug": blog_post.slug}))
        else:
            messages.error(request, "خطا در ارسال فرم. لطفاً فیلدها را بررسی کنید.")
    else:
        form = BlogPostForm()
    return render(request, "blog/create_blog_post.html", {"form": form})

@login_required
def edit_blog_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    if request.user != post.author:
        return HttpResponseForbidden("شما اجازه ویرایش این مقاله را ندارید.")

    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "مقاله با موفقیت ویرایش شد.")
            return redirect(reverse("blog_detail", kwargs={"slug": post.slug}))
        else:
            messages.error(request, "خطا در ارسال فرم. لطفاً فیلدها را بررسی کنید.")
    else:
        form = BlogPostForm(instance=post)

    return render(request, "blog/edit_blog_post.html", {"form": form})

@login_required
def delete_blog_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    if request.user != post.author:
        return HttpResponseForbidden("شما اجازه حذف این مقاله را ندارید.")

    if request.method == "POST":
        post.delete()
        messages.success(request, "مقاله با موفقیت حذف شد.")
        return redirect("blog_list")

    return render(request, "blog/confirm_delete.html", {"post": post})
