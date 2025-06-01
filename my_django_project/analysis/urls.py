# analysis/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.request_analysis_view, name='request_analysis'),
]
