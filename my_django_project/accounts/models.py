import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile') # Added related_name
    referral_code = models.CharField(max_length=20, unique=True, blank=True, null=True) # Allow null temporarily
    referred_by = models.ForeignKey(User, related_name='referrals_made', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        if not self.referral_code:
            # Generate a unique referral code
            self.referral_code = str(uuid.uuid4().hex)[:8].upper()
            # Ensure the generated code is unique
            while Profile.objects.filter(referral_code=self.referral_code).exists():
                self.referral_code = str(uuid.uuid4().hex)[:8].upper()
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create or update the user profile.
    A profile is created for a new user.
    An existing profile is saved whenever the User instance is saved.
    """
    if created:
        Profile.objects.create(user=instance)
    # Ensure profile exists before trying to save, useful for existing users without profiles
    # or if the create signal somehow didn't fire (though it should).
    # However, the above create should handle it.
    # For existing users, their profile might be updated through other means,
    # but saving user instance should also save profile to ensure  or other fields are current.
    # This also ensures referral code is generated if it was missing for an existing user.
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # This case should ideally not be reached if the 'created' signal works for all new User instances.
        # But as a fallback for potentially existing users without profiles from before this signal was in place:
        Profile.objects.create(user=instance)
