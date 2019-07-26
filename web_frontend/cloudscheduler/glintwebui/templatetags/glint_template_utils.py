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


register.filter(name='first_split')
def first_split(value, key):
    """
        Returns the first value of the list after splitting
    """
    return value.split(key)[0]
