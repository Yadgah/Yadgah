# در فایل signals.py
import os

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import UserProfile
from django.db.models.signals import post_save

from django.contrib.auth.models import User  # Import the User model
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()



@receiver(pre_save, sender=UserProfile)
def delete_old_avatar(sender, instance, **kwargs):
    # اگر قبلاً یک تصویر پروفایل وجود داشته باشد و تصویر جدیدی آپلود شده باشد
    if instance.pk:
        old_avatar = UserProfile.objects.get(pk=instance.pk).avatar
        new_avatar = instance.avatar

        # اگر تصویر جدید متفاوت از تصویر قبلی باشد، تصویر قبلی را حذف کن
        if old_avatar and old_avatar != new_avatar:
            if os.path.isfile(old_avatar.path):
                os.remove(old_avatar.path)
