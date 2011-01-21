from django.core.management.base import BaseCommand
from django.conf import settings
from general.settings.models import Setting
from therapyedge import reminders
from datetime import datetime
from optparse import make_option
import gateway

class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('--gateway', default=settings.SMS_GATEWAY_CLASS, dest='gateway',
            help='Specifies the gateway to use, defaults to settings.SMS_GATEWAY_CLASS.'),
    )
    help = "Can be run as a cronjob or directly to send SMS reminders."
    
    def handle(self, *args, **options):
        backend, selected_gateway, sms_receipt_handler = gateway.load_backend(options['gateway'])
        today = datetime.now().date()
        reminders.all(selected_gateway)
        reminders.send_stats(selected_gateway, today)
    