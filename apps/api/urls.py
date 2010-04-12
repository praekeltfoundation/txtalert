from django.conf.urls.defaults import *
from django.http import HttpResponse
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from api.handlers import SMSHandler, PCMHandler, SMSReceiptHandler


http_basic_authentication = HttpBasicAuthentication()

# sms_receipt_handler = Resource(SMSReceiptHandler, http_basic_authentication)
from gateway.backends.opera.views import sms_receipt_handler
sms_handler = Resource(SMSHandler, http_basic_authentication)
pcm_handler = Resource(PCMHandler, http_basic_authentication)

# SMS api
urlpatterns = patterns('',
    url(r'^sms/receipt\.(?P<emitter_format>.+)$', sms_receipt_handler, {}, 'api-sms-receipt'),
    url(r'^sms/(?P<identifier>.+)/(?P<msisdn>[0-9]+)\.(?P<emitter_format>.+)$', sms_handler, {}, 'api-sms'),
    url(r'^sms\.(?P<emitter_format>.+)$', sms_handler, {}, 'api-sms'),
)

# PCM api
urlpatterns += patterns('',
    url(r'^pcm\.(?P<emitter_format>.+)$', pcm_handler, {}, 'api-pcm'),
)