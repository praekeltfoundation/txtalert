from optparse import make_option
import sys

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule
from txtalert.apps import gateway

class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('--gateway', default=settings.SMS_GATEWAY_CLASS, dest='gateway',
            help='Specifies the gateway to use, defaults to settings.SMS_GATEWAY_CLASS.'),
        make_option('--group', default=None, dest='group', 
            help='Specifies the group to send messages for'),
    )
    help = "Can be run as a cronjob or directly to send SMS messages."
    
    def handle(self, *args, **options):
        group_name = options.get('group')
        if not group_name:
            sys.exit('Please provide --group')

        backend, selected_gateway, sms_receipt_handler = gateway.load_backend(options['gateway'])

        # Iterate over installed apps for sender module and call it's handle method.
        for app in settings.INSTALLED_APPS:
            mod = import_module(app)
            try:
                sender = import_module('%s.sender' % app)
                sender.handle(backend, selected_gateway, sms_receipt_handler, group_name)
            except:
                # Decide whether to bubble up this error. If the app just
                # doesn't have a sender module we can ignore the error
                # attempting to import it, otherwise we want it to bubble up.
                if module_has_submodule(mod, 'sender'):
                    raise
