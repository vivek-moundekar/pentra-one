"""
Django settings for udaan project.

Merged from the existing UDAAN project settings.py and the newer settings.py.
All unique settings are preserved and common settings are consolidated.
"""

from pathlib import Path
from decouple import config
from django.utils.translation import gettext_lazy as _
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# ============================================================
# BASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = 'django-insecure-cu&iuy*3oc*%+$b1x=l*jp2zmmzft+-ah%urh@_peu-3221@^k'

GEMINI_API_KEY = config("GEMINI_API_KEY")

GEMINI_API_KEY = config("GEMINI_API_KEY", default="")
HEALTHCARE_GEMINI_API_KEY = config("HEALTHCARE_GEMINI_API_KEY", default="")

DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "10.250.234.83",
]


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Project apps
    'home',
    'accounts',
    'dashboard',
    'education',
    'healthcare',
    'agriculture',
    'government_schemes',
    'women_skills',
    'chatbot',

    # Sites framework
    'django.contrib.sites',

    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

SITE_ID = 1


# ============================================================
# AUTHENTICATION
# ============================================================

# Kept from the newer settings.py.
LOGIN_REDIRECT_URL = '/education/google/complete/'
LOGOUT_REDIRECT_URL = '/education/login/'
LOGIN_URL = "login"
SOCIALACCOUNT_LOGIN_ON_GET = True

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
    }
}

ACCOUNT_TEMPLATE_EXTENSION = "html"


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    # Required for Django multilingual URL/content handling.
    'django.middleware.locale.LocaleMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]


# ============================================================
# URL / TEMPLATES
# ============================================================

ROOT_URLCONF = 'pentraone.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'agriculture.context_processors.agriculture_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'pentraone.wsgi.application'


# ============================================================
# DATABASE
# ============================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", _("English")),
    ("hi", _("हिन्दी")),
    ("mr", _("मराठी")),
    ("gu", _("ગુજરાતી")),
    ("bn", _("বাংলা")),
    ("ta", _("தமிழ்")),
    ("te", _("తెలుగు")),
    ("kn", _("ಕನ್ನಡ")),
    ("pa", _("ਪੰਜਾਬੀ")),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]


# ============================================================
# TIMEZONE
# ============================================================

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True
USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


# ============================================================
# MEDIA FILES
# ============================================================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# EMAIL
# ============================================================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
