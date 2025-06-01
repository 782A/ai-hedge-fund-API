# /app/my_django_project/webapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.models import Group # For is_in_group, though not directly used in this file's views

# View for the public landing page
def landing_page(request):
    if request.user.is_authenticated:
        return redirect('home') # If logged in, redirect to the actual home/dashboard
    return render(request, 'landing_page.html')

# View for the user's home/dashboard page (requires login)
@login_required
def home(request):
    return render(request, 'home.html')

# Helper function to check group membership (can be used by other views)
def is_in_group(user, group_name):
    # Check if user is authenticated before trying to access groups
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()

# View for a premium feature (requires login and group membership)
@login_required
def premium_feature_view(request):
    if is_in_group(request.user, 'PremiumUser'):
        print(f"[DEBUG] User {request.user.username} has access to premium feature.")
        return HttpResponse("Welcome to the Premium Feature!") # Placeholder
    else:
        print(f"[DEBUG] User {request.user.username} does not have access to premium feature.")
        return HttpResponseForbidden("Access Denied. This is a premium feature.") # Placeholder
