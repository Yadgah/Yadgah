import re

import jdatetime
from django import template
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Label

register = template.Library()


@register.filter
def strip_markdown(value):
    """
    Removes Markdown syntax from the input text.
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
    """
    if value:
        # Convert Gregorian date to Jalali
        return jdatetime.date.fromgregorian(date=value).strftime("%d %B")
    return value


@register.filter
def add_class(value, arg):
    """
    Adds a CSS class to a form field widget.
    """
    return value.as_widget(attrs={"class": arg})


@receiver(post_migrate)
def create_default_labels(sender, **kwargs):
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
    for label_name, label_color in labels:
        Label.objects.get_or_create(name=label_name, color=label_color)
