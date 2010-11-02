from datetime import datetime, timedelta, date
from django.core.management.base import BaseCommand
from django.conf import settings
from general.settings.models import Setting
from therapyedge.importer import Importer
from core.models import Clinic
from xml.parsers.expat import ExpatError
import sys, traceback

class Command(BaseCommand):
    help = "Can be run as a cronjob or directly to send import TherapyEdge data."
    def handle(self, *args, **kwargs):
        importer = Importer(
            uri='https://%s:%s@41.0.13.99/tools/ws/sms/patients/server.php' % (
                Setting.objects.get(name='THERAPYEDGE_USERNAME').value,
                Setting.objects.get(name='THERAPYEDGE_PASSWORD').value
            ),
            verbose=settings.DEBUG
        )
        for clinic in Clinic.objects.all():
            # from midnight
            midnight = datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            since = midnight - timedelta(days=1)
            # until 30 days later
            until = midnight + timedelta(days=30)
            print clinic.name, 'from', since, 'until', until
            try:
                for key, value in importer.import_all_changes(
                        clinic, 
                        since=since,
                        until=until
                    ).items():
                    print "\t%s: %s" % (key, value)
            except ExpatError, e:
                print "Exception during processing XML for clinic ", clinic
                traceback.print_exc()
            
                