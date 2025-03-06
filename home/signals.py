import re

import jdatetime
from django import template
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Label

register = template.Library()
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import UserProfile


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


@register.filter
def strip_markdown(value):
    """
    Strips Markdown syntax (like **bold**, *italic*, etc.) from the input text.

    Args:
        value (str): The input string potentially containing Markdown syntax.

    Returns:
        str: The text without Markdown syntax.
    """
    if not isinstance(value, str):
        return value

    # Markdown patterns to remove
    markdown_patterns = [
        r"\*\*(.*?)\*\*",  # Bold (**text**)
        r"\*(.*?)\*",  # Italic (*text*)
        r"__(.*?)__",  # Bold (__text__)
        r"_(.*?)_",  # Italic (_text_)
        r"`(.*?)`",  # Inline code (`code`)
        r"\[(.*?)\]\((.*?)\)",  # Links [text](url)
        r"!\[(.*?)\]\((.*?)\)",  # Images ![alt](url)
        r"^> ",  # Blockquote
        r"#{1,6}\s",  # Headers (#, ##, ###, etc.)
        r"\-\s|\*\s|\+\s",  # Lists (-, *, +)
    ]

    # Remove all patterns from the text
    for pattern in markdown_patterns:
        value = re.sub(pattern, r"\1", value)

    return value.strip()


@register.filter
def jalali_date(value):
    """
    Converts a Gregorian date to a Jalali (Persian) date.

    Args:
        value (datetime.date): The input Gregorian date.

    Returns:
        str: The corresponding Jalali date as a string, e.g., "14 Farvardin".
    """
    if value:
        # Convert Gregorian date to Jalali and format it
        return jdatetime.date.fromgregorian(date=value).strftime("%d %B")
    return value


@register.filter
def add_class(value, arg):
    """
    Adds a CSS class to a form field widget for custom styling.

    Args:
        value (form field widget): The form field to which the class should be added.
        arg (str): The CSS class to be added.

    Returns:
        form field widget: The form field widget with the added class.
    """
    return value.as_widget(attrs={"class": arg})


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
