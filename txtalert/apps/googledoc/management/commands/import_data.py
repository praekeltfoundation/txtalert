from datetime import datetime, timedelta, date
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.conf import settings
from txtalert.apps.general.settings.models import Setting
from txtalert.apps.googledoc.importer import Importer
from txtalert.apps.googledoc.models import SpreadSheet
#from txtalert.core.models import Patient, Visit
import sys, traceback
import os.path
import optparse

class Command(BaseCommand):
    """
    """

    args = '[google spradsheet filename ...]'
    help = 'Can run as Cron job.'

    def handle(self, *args, **kwargs):
        importer = Importer(
            email = Setting.objects.get(name='GOOGLE_EMAIL').value,
            password = Setting.objects.get(name='GOOGLE_PASSWORD').value,
            spreadsheet = Setting.objects.get(name='GOOGLE_SPREADSHEET').value
        )
        
        for spreadsheet in SpreadSheet.objects.all():
             # from midnight
            midnight = datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            start = midnight - timedelta(days=1)
            # until 30 days later
            until = midnight + timedelta(days=30)
            try:
                importer.import_spread_sheet(spreadsheet, start, until)
            except e:
                print "Spreadsheet name exception ", spreadsheet
                traceback.print_exc()
            
            
        
                