from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.conf import settings
from optparse import make_option
from txtalert.apps.general.settings.models import Setting
from txtalert.apps.therapyedge.importer import Importer
from txtalert.core.models import Clinic
import sys

class Command(BaseCommand):
    help = "Can be run as a cronjob or directly to send import TherapyEdge data."
    option_list = BaseCommand.option_list + (
        make_option('--username', dest='username',
            help='Specifies the user to import for.'),
    ) + (
        make_option('--te_ids', dest='te_ids',
            help='Specifies the te_id to test for.'),
    ) + (
        make_option('--days_back', dest='days_back',
            help='Specifies the backward date range offset, default = 1'),
    ) + (
        make_option('--days_forward', dest='days_forward',
            help='Specifies the forward date range offest, default = 30'),
    )

    def handle(self, *args, **kwargs):
        importer = Importer(
            uri='https://%s:%s@41.0.13.99/tools/ws/sms/patients/server.php' % (
                Setting.objects.get(name='THERAPYEDGE_USERNAME').value,
                Setting.objects.get(name='THERAPYEDGE_PASSWORD').value
            ),
            verbose=settings.DEBUG
        )
        username = kwargs.get('username')
        if not username:
            sys.exit('Please provide --username')

        te_ids = kwargs.get('te_ids')
        if not te_ids:
            sys.exit('Please provide --te_ids')
        te_id_list = te_ids.split(',')
        print "\nSearching coming, missed, done and deleted visits for " \
              "te_id's in:\n%s" % repr(te_id_list)

        days_back = int(kwargs.get('days_back') or 1)
        print "From %s days back" % days_back

        days_forward = int(kwargs.get('days_forward') or 30)
        print "to %s days forward\n" % days_forward

        user = User.objects.get(username=username)
        for clinic in Clinic.objects.filter(active=True, user=user):
            print "Clinic name: %s" % clinic.name
            print "Clinic id: %s" % clinic.te_id
            midnight = datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            since = midnight - timedelta(days=days_back)
            until = midnight + timedelta(days=days_forward)
            print "Since: %s" % since
            print "Until: %s" % until
            for v in importer.client.get_coming_visits(clinic.te_id, since, until):
                if v.te_id in te_id_list:
                    print "\t%s" % repr(v)
            for v in importer.client.get_missed_visits(clinic.te_id, since, until):
                if v.te_id in te_id_list:
                    print "\t%s" % repr(v)
            for v in importer.client.get_done_visits(clinic.te_id, since, until):
                if v.te_id in te_id_list:
                    print "\t%s" % repr(v)
            for v in importer.client.get_deleted_visits(clinic.te_id, since, until):
                if v.te_id in te_id_list:
                    print "\t%s" % repr(v)
            print ''
