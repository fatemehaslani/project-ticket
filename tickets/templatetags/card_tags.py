from django import template
from django.utils.html import format_html, conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def card(
        title=None,
        content=None,
        footer=None,
        header=None,
        image_top=None,
        image_bottom=None,
        color="primary",
        outline=False,
        text_center=False,
        extra_class='',
        **kwargs
):
    esc = conditional_escape

    # کلاس‌های اصلی card
    cls = f'card {esc(extra_class)}'.strip()

    # کلاس‌های border و text
    if color:
        if outline:
            cls += f' border-{esc(color)}'
        else:
            cls += f' bg-{esc(color)} text-white'

    if text_center:
        cls += ' text-center'

    # ساخت بخش‌های مختلف card
    header_html = ''
    if header:
        header_html = format_html('<div class="card-header">{}</div>', mark_safe(header))

    footer_html = ''
    if footer:
        footer_html = format_html('<div class="card-footer">{}</div>', mark_safe(footer))

    image_top_html = ''
    if image_top:
        image_top_html = format_html('<img src="{}" class="card-img-top" alt="{}">',
                                     esc(image_top), esc(title or 'Image'))

    image_bottom_html = ''
    if image_bottom:
        image_bottom_html = format_html('<img src="{}" class="card-img-bottom" alt="{}">',
                                        esc(image_bottom), esc(title or 'Image'))

    title_html = ''
    if title:
        title_html = format_html('<h5 class="card-title">{}</h5>', esc(title))

    content_html = ''
    if content:
        content_html = format_html('<div class="card-text">{}</div>', mark_safe(content))

    # ساخت ساختار نهایی
    return format_html(
        '<div class="{}">{} {}<div class="card-body">{}{}</div>{}{}</div>',
        cls,
        mark_safe(header_html),
        mark_safe(image_top_html),
        mark_safe(title_html),
        mark_safe(content_html),
        mark_safe(image_bottom_html),
        mark_safe(footer_html)
    )