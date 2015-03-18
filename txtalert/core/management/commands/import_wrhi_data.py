from django.core.management.base import BaseCommand
from optparse import make_option
from txtalert.wrhi import *
import sys

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--endpoint', default=None, dest='endpoint',
            help='Specifies the endpoint to send the data to'),
    )
    help = "Can be run as a cronjob or directly to fetch and sync wrhi patient information."

    def handle(self, *args, **options):
        endpoint = options.get('endpoint')
        if not endpoint:
            sys.exit('Please provide --endpoint')

        #todo

