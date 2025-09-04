from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a UserProfile automatically when a new User is created.
    """
    if created:
        # Check if the UserProfile table exists before trying to create
        try:
            # This will raise an exception if the table doesn't exist
            UserProfile.objects.get_or_create(user=instance)
        except:
            # If the table doesn't exist yet, just pass
            # The profile will be created when the table is available
            pass

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal to save the UserProfile when the User is saved.
    """
    try:
        # Check if the UserProfile table exists
        UserProfile.objects.get_or_create(user=instance)
        instance.userprofile.save()
    except:
        # If the table doesn't exist yet, just pass
        pass