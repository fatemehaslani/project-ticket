from django import template
from django.utils.html import format_html, conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def col4_2_1(extra_class=None,):
    base_class = 'col-12 col-md-6 col-lg-3'
    if extra_class is None:
        extra_class = []
    else:
        extra_class.append(extra_class)

    output_class = base_class + " ".join(extra_class)
    return format_html(f'<div class="{output_class}"></div>')
