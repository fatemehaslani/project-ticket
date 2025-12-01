from django import template
from django.utils.html import format_html, conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def widget(title, count, color='primary', url=None, icon='', extra_class='', size='sm'):
    esc = conditional_escape

    #size_cls = f' btn-{size}' if size in ('sm', 'lg') else ''

    title_html = ''
    if title:
        title_html = format_html('<h3 class="card-title mb-3>{}</h3>', title)

    if color and color not in ('primary', 'secondary', 'danger', 'info', 'warning', 'success'):
        color = "primary"

    cls = f'card {esc(extra_class)}'.strip()

    count_html = ''
    if count:
        count_html = format_html('<p class="card-text"><span class="badge bg-{} fs-2 rounded-circle">{}</span></p>', esc(color), count)

    icon_html = ''
    if icon:
        icon_html = format_html('<i class="bi bi-{} me-1"></i>', esc(icon))

    link_html = ''
    if url is not None:
        link_html = format_html('<a href="{}" class="btn btn-outline-{}">{}</a>',
                                esc(url), esc(color), 'Red more')
    return format_html(
        '<div class="{}">'
        '<div class="card-body">{} {} {} {}'
        '</div></div>', cls, title_html, count_html, icon_html, link_html,)
