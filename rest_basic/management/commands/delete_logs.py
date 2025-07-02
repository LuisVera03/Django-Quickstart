from django.core.management.base import BaseCommand
from rest_basic.models import UserLog
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Archive old logs'

    def handle(self, *args, **kwargs):
        # borra los logs de usuario más antiguos que 90 días
        threshold = timezone.now() - timedelta(days=90)
        old_logs = UserLog.objects.filter(timestamp__lt=threshold)

        # Eliminar si querés
        old_logs.delete()
        self.stdout.write("Old logs archived and deleted.")

