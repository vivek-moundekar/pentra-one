"""
URL configuration for udaan project.

Merged from the existing UDAAN project urls.py and the newer urls.py.
All unique UDAAN routes are preserved and common configuration is combined.
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # =========================================================
    # DJANGO ADMIN
    # =========================================================

    path(
        "admin/",
        admin.site.urls
    ),


    # =========================================================
    # LANGUAGE SWITCH
    # =========================================================

    path(
        "i18n/",
        include("django.conf.urls.i18n")
    ),


    # =========================================================
    # PUBLIC UDAAN PAGES
    # =========================================================

    path(
        "",
        include("home.urls")
    ),

    path(
        "dashboard/",
        include("dashboard.urls")
    ),


    # =========================================================
    # ACCOUNTS / AUTHENTICATION
    # =========================================================

    path(
        "",
        include("accounts.urls")
    ),

    path(
        "accounts/",
        include("allauth.urls")
    ),

    # Education-specific Google authentication route
    path(
        "education/accounts/",
        include("allauth.urls")
    ),


    # =========================================================
    # MAIN UDAAN MODULES
    # =========================================================

    path(
        "education/",
        include("education.urls")
    ),

    path(
        "healthcare/",
        include("healthcare.urls")
    ),

    path(
        "agriculture/",
        include("agriculture.urls")
    ),

    path(
        "government-schemes/",
        include("government_schemes.urls")
    ),

    path(
        "women-skills/",
        include("women_skills.urls")
    ),

    path(
        "chatbot/",
        include("chatbot.urls")
    ),

]


# =============================================================
# MEDIA FILES
# =============================================================
# Used during local development.
# Teacher-uploaded education videos are served from /media/
# =============================================================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
