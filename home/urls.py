from itertools import chain

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from blog.views import post_list

from .sitemaps import BlogSitemap, QuestionSitemap, StaticViewSitemap
from .views import (
    approve_reply,
    ask_question,
    create_label,
    delete_profile,
    delete_question,
    delete_reply,
    donate,
    edit_question,
    edit_reply,
    explore,
    filter_questions,
    home_view,
    leaderboard,
    login_api,
    login_view,
    logout_view,
    privacy_policy,
    profile_view,
    question_detail,
    robots_txt,
    rules,
    search_view,
    signup_api,
    signup_view,
    slide_detail,
    toggle_reaction,
    user_profile,
)

# Sitemap configuration
sitemaps = {
    "questions": QuestionSitemap,
    "static": StaticViewSitemap,
    "blog": BlogSitemap,
}

# URL patterns grouped by category
user_urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("delete-profile/", delete_profile, name="delete_profile"),
]

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
    path("reply/<int:reply_id>/delete/", delete_reply, name="delete_reply"),
    path("question/<int:question_id>/edit/", edit_question, name="edit_question"),
    path("reply/<int:reply_id>/edit/", edit_reply, name="edit_reply"),
]

info_urlpatterns = [
    path("privacy-policy/", privacy_policy, name="privacy_policy"),
    path("rules/", rules, name="rules"),
]

general_urlpatterns = [
    path("", home_view, name="index"),
    path("leaderboard/", leaderboard, name="leaderboard"),
    path("slide/<slug:slug>/", slide_detail, name="slide_detail"),
    path("explore/", explore, name="explore"),
    path("donate/", donate, name="donate"),
    path("create-label/", create_label, name="create_label"),
    path("search/", search_view, name="search"),
    path("profile/<str:username>/", user_profile, name="user_profile"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("blog/", post_list, name="blog"),
    path("filter-questions/", filter_questions, name="filter_questions"),
]

api_urlpatterns = [
    path("api/signup/", signup_api, name="signup_api"),
    path("api/login/", login_api, name="login_api"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

handler404 = "home.views.custom_page_not_found"
handler500 = "home.views.custom_error"

# Combine all URL patterns
urlpatterns = list(
    chain(
        user_urlpatterns,
        question_urlpatterns,
        info_urlpatterns,
        general_urlpatterns,
        api_urlpatterns,
    )
)

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
