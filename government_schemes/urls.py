from django.urls import path
from . import views

urlpatterns = [
    path('', views.scheme_list, name='scheme_list'),
    path('scheme/<slug:slug>/', views.scheme_detail, name='scheme_detail'),
    path('category/<str:category>/', views.scheme_category, name='scheme_category'),
    path('search/', views.scheme_search, name='scheme_search'),
    path('language/<str:language>/', views.set_scheme_language, name='set_scheme_language'),
]