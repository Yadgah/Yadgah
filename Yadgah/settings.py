"""
Django settings for Yadgah project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see:
    https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see:
    https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

# -------------------------------------------------------------------------
# BASE DIRECTORY
# -------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------------
# SECURITY
# -------------------------------------------------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "some-default-secret-key")
DEBUG = True
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "Yadgah.pythonanywhere.com",
]

# -------------------------------------------------------------------------
# APPLICATION DEFINITION
# -------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "bootstrap5",
    "home",
    "blog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.gzip.GZipMiddleware",
]

ROOT_URLCONF = "Yadgah.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "Yadgah.wsgi.application"

# -------------------------------------------------------------------------
# DATABASE
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# -------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# -------------------------------------------------------------------------
# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
# -------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation." "MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation." "CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation." "NumericPasswordValidator",
    },
]

# -------------------------------------------------------------------------
# INTERNATIONALIZATION
# https://docs.djangoproject.com/en/5.1/topics/i18n/
# -------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------------
# STATIC & MEDIA FILES
# https://docs.djangoproject.com/en/5.1/howto/static-files/
# -------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -------------------------------------------------------------------------
# CACHING
# -------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/var/tmp/django_cache",
    }
}

# -------------------------------------------------------------------------
# AUTHENTICATION
# -------------------------------------------------------------------------
LOGIN_URL = "/login/"
# LOGOUT_REDIRECT_URL = "/"

# -------------------------------------------------------------------------
# DEFAULT PRIMARY KEY FIELD TYPE
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
# -------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
