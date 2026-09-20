from django.db import models
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


class Category(NamedSlugModel):
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "categories"


class Tag(NamedSlugModel):
    pass

    class Meta:
        db_table = "tags"


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

    def __str__(self):
        return f"{self.tracking_code} {self.subject[:30]} ..."


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