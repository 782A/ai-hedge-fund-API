# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.contrib import messages
from django.http import HttpResponse

from .forms import RegistrationForm, UserProfileUpdateForm
from .models import Profile # Import the Profile model

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save() # User is created here

            # Profile is automatically created by the post_save signal.
            # Now process referral code.
            referral_code_used = form.cleaned_data.get('referral_code_used', '').strip().upper()
            if referral_code_used:
                try:
                    referrer_profile = Profile.objects.get(referral_code=referral_code_used)
                    # Ensure user is not referring themselves (profile signal creates blank one first)
                    if referrer_profile.user != user:
                        # Access user.profile; Profile should exist due to post_save signal
                        if hasattr(user, 'profile'):
                            user.profile.referred_by = referrer_profile.user
                            user.profile.save()
                            messages.success(request, f"Successfully registered! You were referred by {referrer_profile.user.username}.")
                            print(f"[DEBUG] User {user.username} was referred by {referrer_profile.user.username}")
                        else:
                            # This case should ideally not happen if signals are working
                            messages.error(request, "Error accessing your profile for referral.")
                            print(f"[ERROR] Profile not found for user {user.username} during referral processing.")
                    else:
                        messages.warning(request, "You cannot use your own referral code.")
                        print(f"[DEBUG] User {user.username} attempted to use own referral code.")
                except Profile.DoesNotExist:
                    messages.warning(request, "Invalid referral code provided, but registration was successful.")
                    print(f"[DEBUG] Invalid referral code '{referral_code_used}' provided.")

            # Assign to FreeUser group (existing logic)
            try:
                free_user_group = Group.objects.get(name='FreeUser')
                user.groups.add(free_user_group)
                print(f'[DEBUG] Added user {user.username} to FreeUser group.')
            except Group.DoesNotExist:
                print(f'[ERROR] FreeUser group does not exist. Cannot assign user {user.username}.')

            # login(request, user) # Optionally log the user in
            # For now, redirect to login page after registration
            messages.info(request, "Registration successful! Please log in.")
            return redirect('login')
    else:
        form = RegistrationForm()

    # For GET request or form errors, render the registration page (conceptually)
    # In a real setup, this would be: return render(request, 'accounts/register.html', {'form': form})
    print(f"[DEBUG] Rendering registration form page (template would be 'accounts/register.html').")
    # Create a simple representation of the form for the HttpResponse
    form_html = "<h1>Register</h1>" + form.as_p() + "<button type='submit'>Register</button>"
    return HttpResponse(f"<div>{form_html}</div>", status=200)


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        # Ensure user.profile exists, which it should due to the signal
        form = UserProfileUpdateForm(instance=request.user)

    # For GET request or form errors, render the profile page (conceptually)
    # In a real setup: return render(request, 'accounts/profile.html', {'form': form, 'user': request.user})
    profile_data_html = f"<p>Username: {request.user.username}</p>"
    if hasattr(request.user, 'profile'):
        profile_data_html += f"<p>Your Referral Code: <strong>{request.user.profile.referral_code}</strong></p>"
        if request.user.profile.referred_by:
            profile_data_html += f"<p>You were referred by: {request.user.profile.referred_by.username}</p>"

        referrals_made_count = request.user.referrals_made.count()
        if referrals_made_count > 0:
            profile_data_html += f"<p>You have referred {referrals_made_count} user(s).</p>"
        else:
            profile_data_html += "<p>You haven't referred anyone yet.</p>"

    form_html = "<h2>Edit Profile</h2>" + form.as_p() + "<button type='submit'>Update</button>"
    return HttpResponse(f"<div>{profile_data_html}{form_html}</div>", status=200)
