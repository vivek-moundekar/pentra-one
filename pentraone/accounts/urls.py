from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),
    path("logout/", views.logout_user, name="logout"),

]