from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from general.settings.models import Settings
from therapyedge.importer import Importer
from core.models import Clinic

class Command(BaseCommand):
    help = "Can be run as a cronjob or directly to send import TherapyEdge data."
    def handle(self, *args, **kwargs):
        importer = Importer(
            uri='https://%s:%s@196.36.218.99/tools/ws/sms/patients/server.php' % (
                Settings.objects.get(name='THERAPYEDGE_USERNAME').value,
                Settings.objects.get(name='THERAPYEDGE_PASSWORD').value
            ),
            verbose=settings.DEBUG
        )
        for clinic in Clinic.objects.all():
            # midnight
            since = datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            
            importer.import_all_changes(
                clinic, 
                since=since,
                until=since + timedelta(days=1)
            )