# /app/my_django_project/api_integration/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('get-analysis/', views.get_stock_analysis, name='get_stock_analysis'),
]
