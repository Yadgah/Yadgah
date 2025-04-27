import re  # Importing the 're' module for regex operations

import jdatetime
from bs4 import BeautifulSoup
from django import template
from django.forms import BoundField

register = template.Library()


@register.filter
def remove_empty_paragraphs(value):
    soup = BeautifulSoup(value, "html.parser")
    for p in soup.find_all("p"):
        if p.get_text(strip=True) == "\xa0":
            p.extract()
    return str(soup)


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

    # Removing all Markdown patterns from the text
    for pattern in markdown_patterns:
        value = re.sub(pattern, r"\1", value)

    return value.strip()


# Filter to convert Gregorian date to Jalali (Persian) date
@register.filter
def jalali_date(value):
    """
    Converts a Gregorian date to a Jalali (Persian) date format.
    """
    if value:
        # Convert the Gregorian date to Jalali
        jalali_date = jdatetime.date.fromgregorian(date=value)
        # Remove leading zero from day and convert to Persian digits
        day = (
            str(jalali_date.day).lstrip("0") or "0"
        )  # Handle case when day is 0 (unlikely)
        # Convert Arabic digits to Persian digits
        persian_digits = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
        day_fa = day.translate(persian_digits)
        # Get month name in Persian
        month_fa = jalali_date.j_months_fa[jalali_date.month - 1]
        return f"{day_fa} {month_fa}"
    return value


# Filter to add a CSS class to a form field widget
@register.filter
def add_class(value, arg):
    """
    Adds a CSS class to the form field widget.
    """
    if isinstance(value, BoundField):
        return value.as_widget(attrs={"class": arg})
    return value  # Return the value unchanged if it's not a BoundField
