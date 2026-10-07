"""
URL configuration for udaan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('home.urls')),
    path('', include('accounts.urls')),

    path('accounts/', include('allauth.urls')),

    path('dashboard/', include('dashboard.urls')),

    path('education/', include('education.urls')),
    path('healthcare/', include('healthcare.urls')),
    path('agriculture/', include('agriculture.urls')),
    path('government-schemes/', include('government_schemes.urls')),
    path('women-skills/', include('women_skills.urls')),
    path('chatbot/', include('chatbot.urls')),
]
