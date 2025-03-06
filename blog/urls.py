from django.urls import path, re_path

from .views import post_create, post_detail, post_list

urlpatterns = [
    path("", post_list, name="post_list"),
    path("create/", post_create, name="post_create"),
    # path("<slug:slug>/", post_detail, name="post_detail"),
    re_path(r"^(?P<slug>[\w-]+)/$", post_detail, name="post_detail"),
]
