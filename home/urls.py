from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.sitemaps.views import sitemap

from .sitemaps import QuestionSitemap, NewsSitemap, StaticViewSitemap
from .views import (
    approve_reply, ask_question, delete_profile, delete_question, explore,
    home_view, leaderboard, login_view, logout_view, mit_license, news_list,
    privacy_policy, profile_view, question_detail, rules, search_view,
    signup_view, toggle_reaction, user_profile, edit_reply, delete_reply, robots_txt, create_label,
)

# Sitemap configuration
sitemaps = {
    "questions": QuestionSitemap,
    "news": NewsSitemap,
    "static": StaticViewSitemap,
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
    path("question/<int:question_id>/toggle-reaction/", toggle_reaction, name="toggle_reaction"),
    path("reply/<int:reply_id>/approve/", approve_reply, name="approve_reply"),
    path("reply/<int:reply_id>/edit/", edit_reply, name="edit_reply"),
    path("reply/<int:reply_id>/delete/", delete_reply, name="delete_reply"),
]

info_urlpatterns = [
    path("privacy-policy/", privacy_policy, name="privacy_policy"),
    path("mit-license/", mit_license, name="mit_license"),
    path("rules/", rules, name="rules"),
]

general_urlpatterns = [
    path("", home_view, name="index"),
    path("news/", news_list, name="news_list"),
    path("leaderboard/", leaderboard, name="leaderboard"),
    path("explore/", explore, name="explore"),
    path("create-label/", create_label, name="create_label"),
    path("search/", search_view, name="search"),
    path("profile/<str:username>/", user_profile, name="user_profile"),

    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
]

# Combine all URL patterns
urlpatterns = user_urlpatterns + question_urlpatterns + info_urlpatterns + general_urlpatterns

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
