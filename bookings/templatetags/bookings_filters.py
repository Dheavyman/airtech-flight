from datetime import datetime

from django.utils.dateparse import parse_datetime
from django.template import Library
from django.template.defaultfilters import stringfilter

register = Library()

@register.filter(name='ctime')
@stringfilter
def custom_time(value):
    value = parse_datetime(value)
    return datetime.strftime(value, '%-I:%M %p')

@register.filter(name='cdate')
@stringfilter
def custom_date(value):
    value = parse_datetime(value)
    return datetime.strftime(value, '%a, %d %b, %Y')
