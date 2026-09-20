from xml.dom import ValidationErr

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.cache import cache

from settings.constants import SITE_SETTINGS_CACHE_KEY


# Create your models here.
class SiteSetting(models.Model):
    site_name = models.CharField(max_length=200)

    tagline = models.CharField(
        max_length=255,
        blank=True
    )

    meta_title = models.CharField(
        max_length=255,
        blank=True
    )

    meta_description = models.TextField(blank=True)

    meta_keywords = models.TextField(blank=True)

    logo = models.ImageField(
        upload_to="settings/",
        blank=True,
        null=True
    )

    favicon = models.ImageField(
        upload_to="settings/",
        blank=True,
        null=True
    )

    facebook = models.URLField(blank=True)

    instagram = models.URLField(blank=True)

    youtube = models.URLField(blank=True)

    email = models.URLField(blank=True)

    phone = models.CharField(
        max_length=11,
        blank=True
    )

    address = models.TextField(blank=True)

    analytics_id = models.CharField(
        max_length=100,
        blank=True
    )

    maintenance_mode = models.BooleanField(default=True)
    enable_registration = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
    )

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        if not self.pk and SiteSetting.objects.exists():
            raise ValidationError(
                "Only one SiteSetting instance is allowed."
            )
        super().save(*args, **kwargs)

        cache.delete(SITE_SETTINGS_CACHE_KEY)

    def delete(self, *args, **kwargs):
        cache.delete(SITE_SETTINGS_CACHE_KEY)

        super().delete(*args, **kwargs)