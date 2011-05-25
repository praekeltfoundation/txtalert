from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
import sys
import logging

class GatewayException(Exception): pass

def load_backend(backend):
    try:
        mod = sys.modules[__name__]
        backend = import_module('.backend', backend)
        setattr(mod, 'backend', backend)
        setattr(mod, 'gateway', backend.gateway)
        setattr(mod, 'sms_receipt_handler', backend.sms_receipt_handler)
        return backend, backend.gateway, backend.sms_receipt_handler
    except ImportError, e:
        raise GatewayException, 'SMS Backend %s does not exist' % backend


load_backend(settings.SMS_GATEWAY_CLASS)
