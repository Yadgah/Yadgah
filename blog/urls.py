from django.urls import path, re_path

from .views import (
    post_create,
    post_delete,
    post_detail,
    post_edit,
    post_list,
    short_link_redirect_by_id,
)

urlpatterns = [
    path("", post_list, name="post_list"),
    path("create/", post_create, name="post_create"),
    path("<slug:slug>/delete/", post_delete, name="post_delete"),
    path("p/<int:pk>/", short_link_redirect_by_id, name="short_link"),
    re_path(r"^(?P<slug>[\w-]+)/$", post_detail, name="post_detail"),
    re_path(r"^(?P<slug>[\w-]+)/edit/$", post_edit, name="post_edit"),
]
