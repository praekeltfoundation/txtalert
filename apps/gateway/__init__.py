import sys, traceback

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

def load_backend(backend):
    try:
        return import_module('.backend', backend)
    except ImportError, e:
        traceback.print_exc(file=sys.stdout)
        raise e

backend = load_backend(settings.SMS_GATEWAY_CLASS)
gateway = backend.gateway
sms_receipt_handler = backend.sms_receipt_handler