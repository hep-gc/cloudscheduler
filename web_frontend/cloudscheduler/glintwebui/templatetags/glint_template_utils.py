from django.template.defaulttags import register
from django.template.defaultfilters import stringfilter
from django.template.defaultfilters import filesizeformat
from django import template

register = template.Library()

@register.filter()
def get_item(template_dict, key):    
    return template_dict.get(key)

@register.filter()
@stringfilter
def strip(value):
    return value.replace(" ", "")


@register.filter()
@stringfilter
def first_split(value, key):
    list = value.split(key)
    return list[0]

@register.filter()
@stringfilter
def filesize_split(value, key):
    list = value.split(key)
    # format file size to human readable format
    if len(list) > 1:
        return filesizeformat(int(list[1]))
    else:
        return '-'
