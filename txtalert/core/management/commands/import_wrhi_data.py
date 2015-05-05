from django.core.management.base import BaseCommand
from optparse import make_option
from txtalert.core.wrhi_automation import import_patients, import_visits
from django.conf import settings
import sys

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--endpoint', default=None, dest='endpoint',
            help='Specifies the endpoint to send the data to'),
    )
    help = "Can be run as a cronjob or directly to fetch and sync wrhi patient information."

    def handle(self, *args, **options):
        endpoint_type = options.get('endpoint')
        if not endpoint_type:
            sys.exit('Please provide --endpoint')

        endpoint = None

        if endpoint_type == 'qa':
            endpoint = settings.WRHI_QA_END_POINT
        elif endpoint_type == 'prod':
            endpoint = settings.WRHI_PROD_END_POINT
        else:
            sys.exit('Invalid endpoint type provided. Options are qa and prod.')

        import_patients(endpoint)
        import_visits(endpoint)