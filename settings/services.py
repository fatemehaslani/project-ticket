from django.core.cache import cache

from .constants import (
    SITE_SETTINGS_CACHE_KEY,
    SITE_SETTINGS_CACHE_TIMEOUT,
)
from .models import SiteSetting

class SiteService:

    @staticmethod
    def settings():
        settings = cache.get(SITE_SETTINGS_CACHE_KEY)

        if settings is None:
            settings = SiteSetting.objects.first()

            cache.set(
                SITE_SETTINGS_CACHE_KEY,
                settings,
                SITE_SETTINGS_CACHE_TIMEOUT,
            )

        return settings