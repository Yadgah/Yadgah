import re

import jdatetime
from django import template
from django.db.models.signals import post_migrate, post_save, pre_save
from django.dispatch import receiver

from blog.models import Post

from .models import Label, UserProfile


@receiver(pre_save, sender=UserProfile)
def delete_old_avatar_on_update(sender, instance, **kwargs):
    # اگر نمونه جدید است (مثلاً هنوز ذخیره نشده)، کاری انجام نده
    if not instance.pk:
        return

    try:
        old_instance = UserProfile.objects.get(pk=instance.pk)
    except UserProfile.DoesNotExist:
        return

    # اگر آواتار تغییر کرده باشد، فایل قبلی را حذف کن
    if old_instance.avatar and old_instance.avatar != instance.avatar:
        old_instance.avatar.delete(save=False)


@receiver(post_migrate)
def create_default_labels(sender, **kwargs):
    """
    Creates default labels after migrations if they don't already exist.

    Default labels are related to various topics such as education, health, etc.
    """
    labels = [
        ("آموزش و یادگیری", "#4CAF50"),
        ("سلامت و پزشکی", "#FF5722"),
        ("فناوری و دیجیتال", "#2196F3"),
        ("هنر و خلاقیت", "#9C27B0"),
        ("کسب‌وکار و کارآفرینی", "#FFC107"),
        ("سفر و گردشگری", "#FF9800"),
        ("روانشناسی و توسعه فردی", "#673AB7"),
        ("علوم و تحقیقات", "#3F51B5"),
        ("سبک زندگی", "#E91E63"),
    ]
    # Create labels if they don't exist
    for label_name, label_color in labels:
        Label.objects.get_or_create(name=label_name, color=label_color)


@receiver(post_save, sender=Post)
def update_user_score(sender, instance, created, **kwargs):
    if created and instance.published:  # تنها در صورت انتشار پست
        user_profile = instance.author.userprofile  # دسترسی به پروفایل کاربر
        user_profile.score += 5  # اضافه کردن 10 امتیاز به کاربر
        user_profile.save()  # ذخیره تغییرات
