from django.urls import path
from . import views, voice

app_name = "agriculture"

urlpatterns = [
    path("", views.agriculture_home, name="home"),

    # Agriculture language
    path(
        "language/",
        views.set_agriculture_language,
        name="set_language",
    ),

    # Crops
    path(
        "crops/",
        views.crop_list,
        name="crops",
    ),

    path(
        "crops/<int:crop_id>/",
        views.crop_detail,
        name="crop_detail",
    ),

    # Crop problems
    path(
        "problems/",
        views.crop_problems,
        name="problems",
    ),

    path(
        "problems/<int:crop_id>/",
        views.crop_problem_detail,
        name="problem_detail",
    ),

    # Weather
    path(
        "weather/",
        views.weather,
        name="weather",
    ),

    # Scan & Ask
    path(
        "scan/",
        views.scan_and_ask,
        name="scan",
    ),

    # Agriculture Voice Agent
    path(
        "voice/",
        voice.voice_tts,
        name="voice",
    ),
]