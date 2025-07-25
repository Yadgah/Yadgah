"""
URL configuration for Yadgah project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from blog.views import post_detail, post_list
from home import views

# # Adds site header, site title, index title to the admin side.
# admin.site.site_header = "Yadgah"
# admin.site.site_title = "Yadgah"
# admin.site.index_title = "Welcome Yadgah"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("home.urls")),
    path("blog/", include("blog.urls")),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "home.views.custom_page_not_found"
handler500 = "home.views.custom_error"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
