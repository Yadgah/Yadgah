from django.urls import path
from .views import blog_list, blog_detail, create_blog_post, edit_blog_post, delete_blog_post

urlpatterns = [
    path("", blog_list, name="blog_list"),
    path("<slug:slug>/", blog_detail, name="blog_detail"),
    path("create/", create_blog_post, name="create_blog_post"),
    path("<slug:slug>/edit/", edit_blog_post, name="edit_blog_post"),
    path("<slug:slug>/delete/", delete_blog_post, name="delete_blog_post"),
]