from datetime import timedelta, date
from django.core.management.base import BaseCommand
from txtalert.apps.googledoc.importer import Importer
from txtalert.apps.googledoc.models import SpreadSheet, GoogleAccount
import logging


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
                    owner=account.user,
                    email=account.username,
                    password=account.password
                )
                for spreadsheet in SpreadSheet.objects.filter(account=account):
                    midnight = date.today()
                    start = midnight - timedelta(days=1)
                    # until 14 days later
                    until = midnight + timedelta(days=14)
                    try:
			print 'spreadhseet', spreadsheet.spreadsheet
                        importer.import_spread_sheet(spreadsheet.spreadsheet,
                                                     start, until)
                        logging.debug("Import spreadsheet data using period.")
                    except:
                        print "Update error for", spreadsheet.spreadsheet
                        logging.exception("Error while updating patient")
        except GoogleAccount.DoesNotExist:
            logging.exception("Google Account does not exists")
            return
