"""
Django settings for UDAAN / Pentra One project.
Cleaned for local development and Render deployment.
"""

from pathlib import Path
from decouple import config
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv
import os

# ============================================================
# BASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# ============================================================
# SECURITY
# ============================================================

# Keep secrets in environment variables on Vercel / Render.
SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-change-this-key-for-production"
)

DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    ".vercel.app",
    ".onrender.com",
]

# Optional platform hostname support.
VERCEL_URL = os.environ.get("VERCEL_URL")
if VERCEL_URL:
    ALLOWED_HOSTS.append(VERCEL_URL)

RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
    "https://*.onrender.com",
]

# API keys
GEMINI_API_KEY = config("GEMINI_API_KEY", default="")
HEALTHCARE_GEMINI_API_KEY = config("HEALTHCARE_GEMINI_API_KEY", default="")


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Project apps
    "home",
    "accounts",
    "dashboard",
    "education",
    "healthcare",
    "agriculture",
    "government_schemes",
    "women_skills",
    "chatbot",

    # Sites framework
    "django.contrib.sites",

    # Allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
]

SITE_ID = 1


# ============================================================
# AUTHENTICATION
# ============================================================

LOGIN_REDIRECT_URL = "/education/google/complete/"
LOGOUT_REDIRECT_URL = "/education/login/"
LOGIN_URL = "login"

SOCIALACCOUNT_LOGIN_ON_GET = True

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    }
}

ACCOUNT_TEMPLATE_EXTENSION = "html"


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "allauth.account.middleware.AccountMiddleware",
]


# ============================================================
# URL / TEMPLATES / WSGI
# ============================================================

# IMPORTANT:
# Your original file says this is the UDAAN Django project.
# Therefore the internal Django project package is assumed to be "udaan".
ROOT_URLCONF = "pentraone.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "agriculture.context_processors.agriculture_context",
            ],
        },
    },
]

WSGI_APPLICATION = "pentraone.wsgi.application"


# ============================================================
# DATABASE
# ============================================================

DATABASE_URL = config("DATABASE_URL", default="")

if DATABASE_URL:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Local development fallback.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
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

# WhiteNoise static file storage
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ============================================================
# MEDIA FILES
# ============================================================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# EMAIL
# ============================================================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# PRODUCTION / VERCEL SECURITY
# ============================================================

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
