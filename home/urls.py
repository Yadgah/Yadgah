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
    ask_question,
    question_detail,
)

# URL patterns for the home app
urlpatterns = [
    path("", home_view, name="index"),  # Home page
    path("signup/", signup_view, name="signup"),  # User signup
    path("login/", login_view, name="login"),  # User login
    path("logout/", logout_view, name="logout"),  # User logout
    path("profile/", profile_view, name="profile"),  # User profile
    path("news/", news_list, name="news_list"),  # News list
    path('ask/', ask_question, name='ask_question'),  # صفحه ارسال سوال
    path('question/<int:question_id>/', question_detail, name='question_detail'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
