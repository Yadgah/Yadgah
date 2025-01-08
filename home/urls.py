from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (
    home_view,
    login_view,
    logout_view,
    news_list,
    profile_view,
    signup_view,
)

urlpatterns = [
    path("", home_view, name="index"),  # صفحه اصلی
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("news/", news_list, name="news_list"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
