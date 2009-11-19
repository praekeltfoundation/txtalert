from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

def load_backend(backend):
    try:
        return import_module('.backend', backend)
    except ImportError, e:
        raise ImproperlyConfigured('Cannot load SMS Gateway Backend: %s' % backend)

backend = load_backend(settings.SMS_GATEWAY_CLASS)
gateway = backend.gateway