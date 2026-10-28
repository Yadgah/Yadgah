from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

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

            # The image is converted to optimized WebP in Post.save()
            # via home.utils.optimize_image_field (#175).
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

            # پردازش تصویر و تبدیل به WebP در Post.save() انجام می‌شود (#175)

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
