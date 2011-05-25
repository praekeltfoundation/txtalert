from django.conf.urls.defaults import *
from django.http import HttpResponse
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from piston.utils import Mimer
from txtalert.apps.api.handlers import (SMSHandler, PCMHandler, 
                                        SMSReceiptHandler, PatientHandler)

# make sure Piston also accepts text/xml with charset=utf-8
Mimer.register(lambda *a: None, ('text/xml; charset=utf-8',))

http_basic_authentication = HttpBasicAuthentication()

sms_receipt_handler = Resource(SMSReceiptHandler, http_basic_authentication)
sms_handler = Resource(SMSHandler, http_basic_authentication)
pcm_handler = Resource(PCMHandler, http_basic_authentication)
patient_handler = Resource(PatientHandler)

# SMS api
urlpatterns = patterns('',
    url(r'^sms/receipt\.(?P<emitter_format>.+)$', sms_receipt_handler, {}, 'api-sms-receipt'),
    url(r'^sms/(?P<identifier>.+)/(?P<msisdn>[0-9]+)\.(?P<emitter_format>.+)$', sms_handler, {}, 'api-sms'),
    url(r'^sms\.(?P<emitter_format>.+)$', sms_handler, {}, 'api-sms'),
    url(r'^patient\.(?P<emitter_format>.+)$', patient_handler, {}, 'api-patient'),
)

# PCM api
urlpatterns += patterns('',
    url(r'^pcm\.(?P<emitter_format>.+)$', pcm_handler, {}, 'api-pcm'),
)