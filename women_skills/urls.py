from django.urls import path
from . import views

urlpatterns = [
    path('', views.women_home, name='women_home'),
    path('skills/', views.skill_list, name='skill_list'),
    path('business/', views.business_ideas, name='business_ideas'),
    path('financial/', views.financial_literacy, name='financial_literacy'),
    path('selling/', views.selling_tips, name='selling_tips'),
    path('progress/', views.my_progress, name='my_progress'),
]