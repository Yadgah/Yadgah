import jdatetime
from django import template

register = template.Library()

# فیلتر برای تبدیل تاریخ میلادی به شمسی
@register.filter
def jalali_date(value):
    if value:
        # تبدیل تاریخ به شمسی
        return jdatetime.date.fromgregorian(date=value).strftime("%d %B")
    return value

@register.filter
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})