from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.conf import settings
from optparse import make_option
from txtalert.apps.general.settings.models import Setting
from txtalert.apps.therapyedge.importer import Importer
from txtalert.core.models import Clinic
from xml.parsers.expat import ExpatError
import sys
import traceback


class Command(BaseCommand):
    help = ("Can be run as a cronjob or directly to send"
            "import TherapyEdge data.")

    option_list = BaseCommand.option_list + (
        make_option('--username', dest='username',
                    help='Specifies the user to import for.'),
        make_option('--start-date', dest='start_date',
                    help='The date to start from'),
        make_option('--days', dest='days',
                    help='The number of days to fetch data for.',
                    default=30, type='int'),
        make_option('--api-url', dest='api_url',
                    help=('The URL of the API to hit. '
                          '{username} and {password} are passed in'
                          'as kwargs to .format()'),
                    default=('https://{username}:{password}@41.0.13.99'
                             '/tools/ws/sms/patients/server.php')),
        make_option('--verbose', dest='verbose', action='store_true'),
    )

    def handle(self, *args, **options):
        url_template = options['api_url']
        url = url_template.format(
            username=Setting.objects.get(name='THERAPYEDGE_USERNAME').value,
            password=Setting.objects.get(name='THERAPYEDGE_PASSWORD').value)

        importer = Importer(uri=url, verbose=options['verbose'])

        username = options.get('username')
        if not username:
            sys.exit('Please provide --username')

        custom_start_date = options.get('start_date')
        if custom_start_date:
            start_date = datetime.strptime(custom_start_date, '%Y-%m-%d')
        else:
            start_date = datetime.now()

        user = User.objects.get(username=username)
        for clinic in Clinic.objects.filter(active=True, user=user):
            # from midnight
            midnight = start_date.replace(hour=0, minute=0, second=0,
                                          microsecond=0)
            since = midnight - timedelta(days=1)
            # until 30 days later
            until = midnight + timedelta(days=options['days'])
            print clinic.name, 'from', since, 'until', until
            try:
                for key, value in importer.import_all_changes(
                        user,
                        clinic,
                        since=since,
                        until=until
                    ).items():
                    print "\t%s: %s" % (key, len(value))
            except ExpatError, e:
                print "Exception during processing XML for clinic ", clinic
                traceback.print_exc()
