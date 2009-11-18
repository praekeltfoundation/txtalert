from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from api.handlers import SMSHandler, PCMHandler


http_basic_authentication = HttpBasicAuthentication()

sms_handler = Resource(SMSHandler, http_basic_authentication)
pcm_handler = Resource(PCMHandler, http_basic_authentication)

urlpatterns = patterns('',
    url(r'^sms\.(?P<emitter_format>.+)$', sms_handler, {}, 'api-sms'),
    url(r'^pcm\.(?P<emitter_format>.+)$', pcm_handler, {}, 'api-pcm'),
)