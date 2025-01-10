import jdatetime
from django import template

register = template.Library()

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
    return value.as_widget(attrs={'class': arg})
