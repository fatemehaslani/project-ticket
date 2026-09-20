from django.core.management import BaseCommand

from tickets.models import Category

class Command(BaseCommand):
    help = 'rest is_active attribute in categories table'


    def handle(self, *args, **options):
        Category.objects.filter(is_active=True).update(is_active=False)

        self.stdout.write(self.style.SUCCESS("\n All categories update\n"))
