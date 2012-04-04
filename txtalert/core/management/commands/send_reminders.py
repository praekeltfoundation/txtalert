from django.core.management.base import BaseCommand
from django.conf import settings
from txtalert.apps.therapyedge import reminders
from datetime import datetime
from optparse import make_option
from txtalert.apps import gateway
import sys

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--gateway', default=settings.SMS_GATEWAY_CLASS, dest='gateway',
            help='Specifies the gateway to use, defaults to settings.SMS_GATEWAY_CLASS.'),
        make_option('--group', default=None, dest='group',
            help='Specifies the group to send reminders for'),
        make_option('--date', default=None, dest='date',
            help='Specify the date (DD/MM/YYYY) to send reminders for, defaults to today.'),
    )
    help = "Can be run as a cronjob or directly to send SMS reminders."

    def handle(self, *args, **options):
        group_name = options.get('group')
        if not group_name:
            sys.exit('Please provide --group')

        backend, selected_gateway, sms_receipt_handler = gateway.load_backend(options['gateway'])
        date_string = options.get('date')
        if date_string:
            today = datetime.strptime(date_string, '%d/%m/%Y').date()
        else:
            today = datetime.now().date()

        reminders.all(selected_gateway, [group_name], today)
        reminders.send_stats(selected_gateway, [group_name], today)
