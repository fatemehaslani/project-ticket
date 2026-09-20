from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.conf import settings
from django.utils.text import slugify, capfirst
from .choices import *


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    class Meta:
        abstract = True


class NamedSlugModel(TimestampedModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        abstract = True


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

        def __str__(self):
            return capfirst(self.name)



class CategoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class Category(NamedSlugModel):
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "categories"

    objects = CategoryQuerySet.as_manager()

    def __str__(self):
        return self.name

class Tag(NamedSlugModel):
    pass

    class Meta:
        db_table = "tags"

    def __str__(self):
        return self.name


class TicketsQuerySet(models.QuerySet):
    def with_priority(self, priority):
        return self.filter(priority=priority)

    def is_close(self):
        return self.filter(closed_at__isnull=False)

    def is_open(self):
        return self.filter(closed_at__isnull=True)

    def is_expired(self):
        pass

    def assigned_by(self, user):
        pass

class Ticket(TimestampedModel):
    category = models.ForeignKey(
        Category,
        related_name="tickets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
     settings.AUTH_USER_MODEL,
        related_name="tickets",
        on_delete=models.PROTECT,
        blank=True,
        default=None,
    )
    priority = models.CharField(max_length=15, choices=PRIORITY_CHOICES, default="low")
    subject = models.CharField(max_length=200)
    #email = models.EmailField(null=True, blank=True)
    #age = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, related_name="tickets", blank=True)
    max_reply_date = models.DateTimeField(help_text="Max reply date")
    closed_at = models.DateTimeField(null=True, blank=True)
    tracking_code = models.CharField(max_length=50, blank=True, null=True, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["priority"]),
        ]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)  #save first to get primary key
        if is_new and not self.tracking_code:
            self.tracking_code = f"TCK-{now().strftime('%Y%m%d')}-{self.pk:05d}"
            super().save(update_fields=["tracking_code"])

    def get_priority_color(self):
        return PRIORITY_COLORS.get(self.priority, "#6c757d")

    def get_edit_url(self):
        return reverse('tickets-update', args=[self.pk])

    def get_absolute_url(self):
        return reverse('tickets-detail', args=[self.pk])

    def get_delete_url(self):
        return reverse('tickets-delete', args=[self.pk])

    def get_ticket_url(self):
        return reverse('tickets', args=[self.pk])

    def __str__(self):
        return f"{self.tracking_code} {self.subject[:30]} ..."


    objects = TicketsQuerySet.as_manager()


class AssignmentQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(assignee=user)

    def open(self):
        return self.filter(status__in=["new", "in_progress"])

class Assignment(TimestampedModel):
    assigned_ticket = models.ForeignKey(
        Ticket,
        related_name="assignments",
        on_delete=models.CASCADE,
        help_text="Ticket to assign"
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assignments",
        on_delete=models.CASCADE,
        help_text="User to whom this assignment was assigned"
    )
    seen_at = models.DateTimeField(null=True, blank=True, help_text="When this assigment was seen by assignee?")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="new")
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["assigned_ticket", "assignee"], name="unique_ticket_assignee")
        ]

    def get_status_color(self):
        return STATUS_COLORS.get(self.status, "#6c757d")

    def __str__(self):
        return f'{self.assigned_ticket.subject} assigned to {self.assignee.username}'

    objects = AssignmentQuerySet.as_manager()

class SearchLog(models.Model):
    search_subject = models.CharField(max_length=1024)
    search_category = models.CharField(max_length=200)
    search_priority = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="search_logs",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        editable=False,
    )

    class Meta:
        db_table = "search_logs"

        permissions = [
            ('search_log_export', "Can export tickets")
        ]

    def __str__(self):
        output = f'at {self.created_at}'
        if self.user is not None:
            return output + f' by {self.user.username}'
        else:
            return output + ' by guest'

class Attachment(TimestampedModel):
    ticket = models.ForeignKey(
        "Ticket",
        related_name="attachments",
        on_delete=models.CASCADE
    )
    file = models.FileField(upload_to="ticket_attachments/%Y/%m/%d/")


    def __str__(self):
        return self.file.name


class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ("view", "View"),
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("status_change", "Status Change"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="activities"
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    field = models.CharField(max_length=100, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Role(models.Model):
    title = models.CharField(max_length=100)
    persian_title = models.CharField(max_length=100)


class UserRole(TimestampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="user_roles",
        on_delete=models.CASCADE,
        blank=True,
    )

    role = models.ForeignKey(Role, on_delete=models.CASCADE, blank=True)

    class Meta:
        db_table = "role_user"