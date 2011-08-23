from datetime import datetime, timedelta, date
from django.core.management.base import BaseCommand
from django.conf import settings
from txtalert.apps.googledoc.importer import Importer
from txtalert.apps.googledoc.models import SpreadSheet, GoogleAccount
import logging
import sys, traceback
import os.path
import optparse

logger = logging.getLogger("import_data")

class Command(BaseCommand):
    help = 'Can run as Cron job  or directly to send import google spreadsheet data.'
    def handle(self, *args, **kwargs):
        try:
            for account in GoogleAccount.objects.all():
               importer = Importer(
                   email = account.username,
                   password = account.password
               )
               try:
                   #get the spreadsheet for this acount holder
                   spreadsheet = SpreadSheet.objects.get(account=account)
                except SpreadSheet DoesNotExist:
                    logger.exception("Spreadsheet for account: %s not avalaible\n" % account)
                    return
               # from midnight
               midnight = datetime.now().replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0
               )
               start = midnight - timedelta(days=1)
               # until 14 days later
               until = midnight + timedelta(days=14)
               try:
                   importer.import_spread_sheet(spreadsheet, start, until)
               except:
                   print "Spreadsheet name exception ", spreadsheet
                   traceback.print_exc()
        except GoogleAccount.DoesNotExist as gerror:
            logger.exception("Google Account does not exists")
            traceback.print_exc()
            return
       
                