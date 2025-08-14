
from django.core.management.base import BaseCommand
from rest_basic.models import UserLog
from django.utils.timezone import now
from datetime import timedelta


class Command(BaseCommand):
    help = 'Delete user logs older than 90 days.'

    def handle(self, *args, **options):
        """Delete UserLog entries older than 90 days."""
        threshold = now() - timedelta(days=90)
        deleted_count, _ = UserLog.objects.filter(timestamp__lt=threshold).delete()
        self.stdout.write(self.style.SUCCESS(f"{deleted_count} old user logs deleted."))

