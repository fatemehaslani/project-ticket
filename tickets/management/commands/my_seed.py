from django.core.management import BaseCommand

class Command(BaseCommand):
    help = 'concatenate'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, default='Ali', help='The name of user')
        parser.add_argument('--name2', type=str, default='reza', help='The name of user')

    def handle(self, *args, **options):
        s = options['name']
        s += options['name2']

        self.stdout.write(self.style.SUCCESS(s))