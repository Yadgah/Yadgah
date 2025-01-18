import re

import jdatetime
import markdown
from django import template

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


# @register.filter(name='markdown')
# def markdown_to_html(value):
#     """Filter to convert Markdown to HTML."""
#     return markdown.markdown(value)


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


# home/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Label


@receiver(post_migrate)
def create_default_labels(sender, **kwargs):
    labels = [
        ("Linux", "#ff6347"),
        ("Python", "#306998"),
        ("PHP", "#4f5b93"),
        ("JavaScript", "#f0db4f"),
        ("Django", "#092e20"),
    ]
    for label_name, label_color in labels:
        Label.objects.get_or_create(name=label_name, color=label_color)
