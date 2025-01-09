# در فایل signals.py
import os

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import UserProfile


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
