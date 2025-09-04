from django import template
import re

register = template.Library()

@register.filter
def regex_replace(value, arg):
    if not value:
        return ""
    try:
        pattern, replacement = arg.split(':', 1)
        return re.sub(pattern, replacement, str(value))
    except (ValueError, re.error):
        return str(value)