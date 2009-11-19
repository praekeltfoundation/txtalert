from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

def load_gateway(backend):
    try:
        return import_module('.backend', backend).gateway
    except ImportError, e:
        raise ImproperlyConfigured('Cannot load SMS Gateway Backend: %s' % backend)

gateway = load_gateway(settings.SMS_GATEWAY_CLASS)