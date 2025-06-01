# accounts/urls.py
from django.urls import path
from . import views # For the register view and profile view
from django.contrib.auth import views as auth_views # For LoginView, LogoutView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
    path('profile/', views.profile, name='profile'), # Added profile path
]
