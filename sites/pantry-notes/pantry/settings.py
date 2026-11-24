"""Settings for Pantry Notes, a recipe site served by Django on port 3107.

The site has no database: the shopping list lives in a signed-cookie session, and
submitted recipes are kept in memory until the server restarts.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# A fixed development key; set PANTRY_SECRET_KEY to override it.
SECRET_KEY = os.environ.get("PANTRY_SECRET_KEY", "pantry-notes-local-only-key-0e7d1c4b9a")
DEBUG = os.environ.get("PANTRY_DEBUG", "") == "1"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "recipes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "pantry.urls"
WSGI_APPLICATION = "pantry.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "recipes.context.shopping_list",
            ],
        },
    },
]

DATABASES = {}
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True
MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = False
USE_TZ = True

STATIC_URL = "/static/"
# The app's static folder, served directly (see pantry/urls.py).
STATIC_DIR = BASE_DIR / "recipes" / "static"
