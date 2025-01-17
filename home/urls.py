from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (approve_reply, ask_question, delete_profile, home_view,
                    load_questions, login_view, logout_view, news_list,
                    profile_view, question_detail, signup_view,
                    toggle_reaction, user_profile)

# URL patterns for the home app
urlpatterns = [
    path("", home_view, name="index"),  # Home page
    path("signup/", signup_view, name="signup"),  # User signup
    path("login/", login_view, name="login"),  # User login
    path("logout/", logout_view, name="logout"),  # User logout
    path("profile/", profile_view, name="profile"),  # User profile
    path("news/", news_list, name="news_list"),  # News list
    path("ask/", ask_question, name="ask_question"),  # Ask a question
    path("question/<int:question_id>/", question_detail, name="question_detail"),  # Question details
    path(
        "load-questions/", load_questions, name="load_questions"
    ),  # Load more questions with pagination
    path("profile/<str:username>/", user_profile, name="user_profile"),  # User profile by username
    path("delete-profile/", delete_profile, name="delete_profile"),  # Delete user profile
    path("question/<int:question_id>/toggle-reaction/",toggle_reaction,name="toggle_reaction",),  # Toggle reaction
    path("reply/<int:reply_id>/approve/", approve_reply, name="approve_reply"),  # Approve a reply
    path('load/', load_questions, name='load'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
