from django.core.management import BaseCommand

from tickets.factories import (
    CategoryFactory, TagFactory
)

class Command(BaseCommand):
    help = 'seed database with sample data'

    def add_arguments(self, parser):
        parser.add_argument("--categories", type=int, default=1, help="Number of categories")
        parser.add_argument("--tags", type=int, default=3, help="Number of tags")

    def handle(self, *args, **options):
        categories = CategoryFactory.create_batch(options["categories"])
        tags = TagFactory.create_batch(options["tags"])

        self.stdout.write(self.style.SUCCESS(f'{len(categories)} categories added.\n'))
        self.stdout.write(self.style.SUCCESS(f'{len(tags)} tags added.\n'))