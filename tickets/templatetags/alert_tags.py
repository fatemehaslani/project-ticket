from django import template
from django.utils.html import format_html, conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def alert(message,
          alert_type="info",
          dismissible=True,
          icon=None,
          extra_class='',
          close_label="Clos",
          heading=None):

    esc = conditional_escape

    # تعیین نوع alert
    if alert_type not in ('primary', 'secondary', 'success', 'danger',
                          'warning', 'info', 'light', 'dark'):
        alert_type = "info"

    # کلاس‌های اصلی
    cls = f'alert alert-{esc(alert_type)} {esc(extra_class)}'.strip()

    # دکمه بستن - اینجا داخل کامپوننت قرار می‌دهیم
    close_button = ''
    if dismissible:
        cls += ' alert-dismissible fade show'
        close_button = '''
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        '''
        esc(close_label)

    # آیکون (اختیاری)
    icon_html = ''
    if icon:
        icon_html = format_html('<i class="bi {} me-2"></i>', esc(icon))

    # هدینگ (اختیاری)
    heading_html = ''
    if heading:
        heading_html = format_html('<h4 class="alert-heading">{}</h4>', esc(heading))

    # ساخت ساختار نهایی - دکمه بستن اینجا اضافه می‌شود
    return format_html(
        '<div class="{}" role="alert">{} {}{} {}</div>',
        cls,
        mark_safe(icon_html),
        mark_safe(heading_html),
        esc(message),
        mark_safe(close_button)
    )