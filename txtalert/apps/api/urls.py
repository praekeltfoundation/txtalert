from django.conf.urls.defaults import *
from django.http import HttpResponse
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from piston.utils import Mimer
from txtalert.apps.api.handlers import (SMSHandler, PCMHandler,
                                        SMSReceiptHandler, PatientHandler,
                                        ChangeRequestHandler, CallRequestHandler)

# make sure Piston also accepts text/xml with charset=utf-8
Mimer.register(lambda *a: None, ('text/xml; charset=utf-8',))

http_basic_authentication = HttpBasicAuthentication()


# FIXME: Fix for newer djangos, piston needs to go away.
class CSRFExemptResource(Resource):
    csrf_exempt = False



sms_receipt_handler = CSRFExemptResource(SMSReceiptHandler, http_basic_authentication)
sms_handler = CSRFExemptResource(SMSHandler, http_basic_authentication)
pcm_handler = CSRFExemptResource(PCMHandler, http_basic_authentication)
patient_handler = CSRFExemptResource(PatientHandler)
change_request_handler = CSRFExemptResource(ChangeRequestHandler, http_basic_authentication)
call_request_handler = CSRFExemptResource(CallRequestHandler, http_basic_authentication)

# SMS api
urlpatterns = patterns('',
    url(r'^sms/receipt\.(?P<emitter_format>.+)$', sms_receipt_handler, {}, 'api-sms-receipt'),
    url(r'^sms/(?P<identifier>.+)/(?P<msisdn>[0-9]+)\.(?P<emitter_format>.+)$', sms_handler, {}, 'api-sms'),
    url(r'^sms\.(?P<emitter_format>.+)$', sms_handler, {}, 'api-sms'),
    url(r'^patient\.(?P<emitter_format>.+)$', patient_handler, {}, 'api-patient'),
    url(r'^request/change\.(?P<emitter_format>.+)$', change_request_handler, {}, 'api-req-change'),
    url(r'^request/call\.(?P<emitter_format>.+)$', call_request_handler, {}, 'api-req-call'),
)

# PCM api
urlpatterns += patterns('',
    url(r'^pcm\.(?P<emitter_format>.+)$', pcm_handler, {}, 'api-pcm'),
)