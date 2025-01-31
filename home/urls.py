from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (
    approve_reply,
    ask_question,
    delete_profile,
    delete_question,
    explore,
    home_view,
    leaderboard,
    login_view,
    logout_view,
    mit_license,
    news_list,
    privacy_policy,
    profile_view,
    question_detail,
    rules,
    search_view,
    signup_view,
    toggle_reaction,
    user_profile,
)

# Define URL patterns for user-related actions
user_urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("delete-profile/", delete_profile, name="delete_profile"),
]

# Define URL patterns for questions and interactions
question_urlpatterns = [
    path("ask/", ask_question, name="ask_question"),
    path("question/<int:question_id>/", question_detail, name="question_detail"),
    path("question/<int:question_id>/delete/", delete_question, name="delete_question"),
    path(
        "question/<int:question_id>/toggle-reaction/",
        toggle_reaction,
        name="toggle_reaction",
    ),
    path("reply/<int:reply_id>/approve/", approve_reply, name="approve_reply"),
]

# Define URL patterns for information and static content
info_urlpatterns = [
    path("privacy-policy/", privacy_policy, name="privacy_policy"),
    path("mit-license/", mit_license, name="mit_license"),
    path("rules/", rules, name="rules"),
]

# Define URL patterns for general navigation
general_urlpatterns = [
    path("", home_view, name="index"),
    path("news/", news_list, name="news_list"),
    path("leaderboard/", leaderboard, name="leaderboard"),
    path("explore/", explore, name="explore"),
    path("search/", search_view, name="search"),
    path("profile/<str:username>/", user_profile, name="user_profile"),
]

# Combine all URL patterns into one list
urlpatterns = (
    user_urlpatterns
    + question_urlpatterns
    + info_urlpatterns
    + general_urlpatterns
)

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
