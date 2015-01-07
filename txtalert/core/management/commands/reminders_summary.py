from optparse import make_option
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from txtalert.apps import gateway
from txtalert.apps.therapyedge import reminders


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option(
            '--group', default=None, dest='group',
            help='Specifies the group to send reminders for'),
        make_option(
            '--date', dest='date',
            help='Date for which to print the summary.'),
        make_option(
            '--clinic-name', default=None, dest='clinic_name',
            help="Specify the clinic's name to send reminders for. "
                 "(optional, defaults to all clinics for the group)"),
    )
    DATE_FORMAT = '%d/%m/%Y'

    def handle(self, *args, **options):
        group_name = options.get('group')
        date_string = options.get('date')
        if not all([group_name, date_string]):
            raise CommandError('Please provide --group and --date')

        gateway_info = gateway.load_backend(
            'txtalert.apps.gateway.backends.debug')
        backend, selected_gateway, sms_receipt_handler = gateway_info

        today = datetime.strptime(date_string, self.DATE_FORMAT).date()
        clinic_name = options.get('clinic_name')

        reminders.all(selected_gateway, [group_name], today, clinic_name)
