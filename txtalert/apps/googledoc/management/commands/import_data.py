from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from txtalert.apps.googledoc.importer import Importer
from txtalert.apps.googledoc.models import SpreadSheet, GoogleAccount
import logging
import traceback

logger = logging.getLogger("import_data")

class Command(BaseCommand):

    
    """ The program access the accounts in the GoogleAccount Table
        for each account a spreadsheet associated with it is imported.
        The account details are sent to import module; these are used
        to login to the user's google account to access the spreadsheet
        with appointment information."""
    help = 'Can run as Cron job or directly to import google spreadsheet data.'
    def handle(self, *args, **kwargs):
        try:
            for account in GoogleAccount.objects.all():
                importer = Importer(
                    email=account.username,
                    password=account.password
                )
                try:
                    #get the spreadsheet for this acount holder
                    spreadsheet = SpreadSheet.objects.get(account=account)
                except SpreadSheet.DoesNotExist, MultipleObjectsReturned:
                    logger.exception("No Spreadsheet for account: %s\n" %
                                      account)
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
                    importer.import_spread_sheet(spreadsheet.spreadsheet,
                                                 start, until)
                except:
                    print "Spreadsheet name invalid ", spreadsheet.spreadsheet
                    traceback.print_exc()
        except GoogleAccount.DoesNotExist:
            logger.exception("Google Account does not exists")
            traceback.print_exc()
            return
