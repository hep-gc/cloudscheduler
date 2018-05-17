from django.template.defaulttags import register
from django.template.defaultfilters import stringfilter
from django import template

register = template.Library()

@register.filter()
def get_item(template_dict, key):    
    return template_dict.get(key)

@register.filter
@stringfilter
def strip(value):
    return value.replace(" ", "")