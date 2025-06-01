"""
URL configuration for webapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from . import views as webapp_project_views # webapp.views for landing_page and home (dashboard)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('api/', include('api_integration.urls')),
    path('analysis/', include('analysis.urls')),

    path('', webapp_project_views.landing_page, name='landing_page'), # Root URL for public landing page
    path('home/', webapp_project_views.home, name='home'),           # Explicit URL for user dashboard

    path('premium-feature/', webapp_project_views.premium_feature_view, name='premium_feature'),
]
