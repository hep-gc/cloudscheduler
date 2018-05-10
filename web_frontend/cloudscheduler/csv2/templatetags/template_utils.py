from django.template.defaulttags import register
from django.template.defaultfilters import stringfilter
from django import template

register = template.Library()

@register.filter
def keyvalue(dict, key):    
    return dict[key]      