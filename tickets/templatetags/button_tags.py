from django import template
from django.utils.html import format_html, conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def button(label,
           url=None,
           color="primary",
           outline=False,
           icon=None,
           type="link",
           size="sm",
           extra_class='',
           confirm=None):

    esc = conditional_escape

    size_cls = f' btn-{size}' if size in ('sm', 'lg') else ''


    if color and color not in ('primary', 'secondary', 'danger'):
        color = "primary"

    cls = f'btn btn-{esc(color)}{size_cls} {esc(extra_class)}'.strip()

    icon_html = ''
    if icon:
        icon_html = format_html('<i class="bi {} me-1"></i>', esc(icon))

    if url and type == 'link':
        return format_html('<a href="{}" class="{}">{}</a>',
                           esc(url), cls, mark_safe(icon_html + esc(label)))
    else:
        confirm_attr = ''
        if confirm:
            confirm_js = f"return confirm({format_html('{}', esc(confirm))});"
            btn_type = esc(type) if type else 'submit'
            return format_html('<button type="{}" class="{}"{}</button>',
                               btn_type, cls, confirm_attr, mark_safe(icon_html + esc(label)))