import jdatetime
import markdown
from django import template
from django.forms import BoundField
register = template.Library()


@register.filter
def strip_markdown(value):
    """
    حذف علائم Markdown از متن ورودی.
    """
    if not isinstance(value, str):
        return value

    # الگوهای Markdown برای حذف
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

    # حذف تمام الگوها از متن
    for pattern in markdown_patterns:
        value = re.sub(pattern, r"\1", value)

    return value.strip()


# @register.filter(name='markdown')
# def markdown_to_html(value):
#     """فیلتر برای تبدیل Markdown به HTML"""
#     return markdown.markdown(value)


# Filter to convert Gregorian date to Jalali (Persian) date
@register.filter
def jalali_date(value):
    if value:
        # Convert Gregorian date to Jalali
        return jdatetime.date.fromgregorian(date=value).strftime("%d %B")
    return value


# Filter to add a CSS class to a form field widget
@register.filter
def add_class(value, arg):
    if isinstance(value, BoundField):
        return value.as_widget(attrs={"class": arg})
    return value  # Return the value unchanged if it's not a BoundField
