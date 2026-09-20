from django.core.cache import cache
from django.core.management.base import BaseCommand

from settings.constants import SITE_SETTINGS_CACHE_KEY, SITE_SETTINGS_CACHE_TIMEOUT
from settings.models import SiteSetting

class Command(BaseCommand):
    help = 'Initialize site settings'

    def handle(self, *args, **options):
        if not SiteSetting.objects.exists():
            SiteSetting.objects.create(
                site_name="My Awesome Website",
                meta_title="My Awesome Website title",
                meta_description="This is my awesome website description",
                meta_keywords="Ticket,key2,key3,key4,key5",
            )

            settings = SiteSetting.objects.first()

            cache.set(
                SITE_SETTINGS_CACHE_KEY,
                settings,
                SITE_SETTINGS_CACHE_TIMEOUT,
            )

            self.stdout.write(self.style.SUCCESS('Site settings created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Site settings already exist'))