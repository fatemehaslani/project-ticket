from django.core.management import BaseCommand, CommandError
from django.db.migrations.recorder import MigrationRecorder
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Laravel-like migration helper for rollback, reset, status'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="action", help="Action to perform")

        rollback_parser = subparsers.add_parser("rollback", help="Rollback migrations")
        rollback_parser.add_argument(
            "--steps",
            type=int,
            default=1,
            help="Number of migration steps to rollback"
        )

        #reset
        subparsers.add_parser("reset", help="Reset all migrations")

        #Status
        subparsers.add_parser("status", help="Show migration status")

    def handle(self, *args, **options):
            action = options.get("action")
            if action == "rollback":
                self.rollback(steps=options.get("steps"))
            elif action == "reset":
                self.reset()
            elif action == "status":
                self.status()
            else:
                raise CommandError("Invalid action.Choose rollback, reset, or status.")

        def rollback(self, steps=1):
            applied = MigrationRecorder.Migration.objects.all().order_by('-applied')
            if not applied.exists():
                self.stdout.write("No migration applied.")
                return

            apps_seen = []
            migrations_to_rollback = []
            for mig in applied:
                if mig.app not in apps_seen:
                    apps_seen.append(mig.app)
                if len(apps_seen) > steps:
                    break
                migrations_to_rollback.append((mig.app, mig.name))
            for app, name in migrations_to_rollback:
                self.stdout.write(f"Rolling back {app} -> {name} ...")
                call_command("migrate", app, name)

        def reset(self):
            recorder = MigrationRecorder.Migration.objects.all()
            apps = recorder.values_list("app", flat=True).distinct()
            for app in apps:
                self.stdout.write(f"Resetting {app}...")
                call_command("migrate", app, "zero")


        def status(self):
            call_command("showmigrations")
