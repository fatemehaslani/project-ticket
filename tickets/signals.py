from django.conf import settings
from django.contrib.messages.context_processors import messages
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from .middleware import get_current_user, get_current_ip
from .models import Ticket, ActivityLog
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail


@receiver(pre_save, sender=Ticket)
def log_ticket_changes(sender, instance, **kwargs):
    if not instance.pk:
        return

    old = Ticket.objects.get(pk=instance.pk)
    user = get_current_user()
    ip = get_current_ip()

    tracked_fields = ["priority", "subject", "description"]

    for field in tracked_fields:
        old_value = getattr(old, field)
        new_value = getattr(instance, field)

        if old_value != new_value:
            ActivityLog.objects.create(
                user=user,
                ticket=instance,
                #action="status_change" if field == "status" else "update",
                action="update",
                field=field,
                old_value=str(old_value),
                new_value=str(new_value),
                ip_address=ip,
            )


@receiver(post_save, sender=Ticket)
def ticket_send_email_notification(sender, instance, created, **kwargs):
    if created:
        subject = f"A new Ticket created: #{instance.id}"
        html_template = "emails/ticket_create.html"
        text_template = "emails/ticket_create.txt"
    else:
        subject = f"A new Ticket created: #{instance.id}"
        html_template = "emails/ticket_create.html"
        text_template = "emails/ticket_create.txt"

    context = {
        "title": instance,
        "creator": instance.created_by,
        "ticket_url": f"http://127.0.0.1:8000/tickets/{instance.id}",
    }
    html_content = render_to_string(html_template, context)
    text_content = render_to_string(text_template, context)
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=None,
        to=["fatemehaslani0083@gmail.com"],
    )

    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)

#@receiver(post_save, sender=Ticket)
#def ticket_send_email_notification(sender, instance, created, **kwargs):
#    if created:
#        subject = f"A new Ticket created: #{instance.id}"
#        message = (
#            f"A new has been Ticket created: #{instance.id}\n\n"
#            f"Title: {instance.subject}\n\n"
#            f"Description: {instance.description}\n\n"
#            f"max_reply_date: {instance.max_reply_date}\n\n"
#            f"Creator: {instance.created_by.username}\n\n"
#        )
#        send_mail(
#            subject=subject,
#            message=message,
#            from_email=None,
#            recipient_list=["fatemehaslani0083@gmail.com"],
#            fail_silently=False,
#        )

@receiver(post_save, sender=Ticket)
def ticket_created_or_updated(sender, instance, created, **kwargs):
    if created:
        print(f" >> New Ticket created: {instance.subject}")
    else:
        print(f" >> Ticket updated: {instance.subject}")

@receiver(post_delete, sender=Ticket)
def ticket_deleted(sender, instance, **kwargs):
    print(f" >> Ticket deleted: {instance.subject}")