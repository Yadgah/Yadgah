import os

from django.contrib.auth.models import User  # Import the User model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import UserProfile


# Signal to create a UserProfile when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# Signal to save the UserProfile whenever the User instance is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


# Signal to delete the old avatar image if a new one is uploaded
@receiver(pre_save, sender=UserProfile)
def delete_old_avatar(sender, instance, **kwargs):
    if instance.pk:
        old_avatar = UserProfile.objects.get(pk=instance.pk).avatar
        new_avatar = instance.avatar

        # If a new avatar is different from the old one, delete the old one
        if old_avatar and old_avatar != new_avatar:
            if os.path.isfile(old_avatar.path):
                os.remove(old_avatar.path)
