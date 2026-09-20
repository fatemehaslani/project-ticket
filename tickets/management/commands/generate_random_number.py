from django.core.management import BaseCommand
import random


class Command(BaseCommand):
    help = 'a random two-digit integar'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='number of random numbers to generate (default=1)'
        )

    def handle(self, *args, **options):
        count = options['count']

        for i in range(count):
            random_number = random.randint(10, 99)

            self.stdout.write(self.style.SUCCESS(f'Random two-digit number: {random_number}'))

            if count > 1 and i < count - 1:
                self.stdout.write('---')