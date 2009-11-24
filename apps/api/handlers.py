from django.contrib.auth.decorators import permission_required
from django.utils import simplejson
from django.http import HttpResponse

from piston.handler import BaseHandler
from piston.utils import rc, require_mime, throttle

from gateway.backends.opera.utils import process_receipts_xml
from gateway.models import SendSMS, PleaseCallMe

from gateway import gateway

from datetime import datetime
import logging
import iso8601

class SMSHandler(BaseHandler):
    allowed_methods = ('POST', 'GET')
    fields = ('identifier', 'delivery', 'expiry', 'delivery_timestamp', 
                'status', 'status_display', 'msisdn')
    model = SendSMS
    
    # Fixme, the way I deal with one resource & a list of resource in one view
    # is hideous
    @permission_required('gateway.can_view_sms_statistics')
    @throttle(10, 60)
    def read(self, request, msisdn=None, identifier=None):
        if all([msisdn, identifier]):
            return self._read_one(msisdn, identifier)
        else:
            return self._read_list(request)
    
    def _read_list(self, request):
        if 'since' in request.GET:
            since = iso8601.parse_date(request.GET['since'])
            return SendSMS.objects.filter(delivery__gte=since)
        else:
            return rc.BAD_REQUEST
    
    def _read_one(self, msisdn, identifier):
        return SendSMS.objects.get(msisdn=msisdn, identifier=identifier)
    
    @permission_required('gateway.can_send_sms')
    @throttle(10, 60)
    @require_mime('json')
    def create(self, request):
        if request.content_type:
            msisdns = request.data.get('msisdns',[])
            smstext = request.data.get('smstext','')
            if len(smstext) <= 160 and len(msisdns) > 0:
                return gateway.send_sms(msisdns, (smstext,) * len(msisdns))
        return rc.BAD_REQUEST
    
    @classmethod
    def status_display(self, instance):
        return instance.get_status_display()
    

class SMSReceiptHandler(BaseHandler):
    allowed_methods = ('POST')
    
    # @permission_required('gateway.can_place_sms_receipt')
    # @require_mime('xml')
    def create(self, request):
        success, fail = process_receipts_xml(request.raw_post_data)
        return HttpResponse(simplejson.dumps({
            'success': map(lambda rcpt: rcpt._asdict(), success),
            'fail': map(lambda rcpt: rcpt._asdict(), fail)
        }), status=201, content_type='application/json; charset=utf-8')
    

class PCMHandler(BaseHandler):
    allowed_methods = ('POST', 'GET')
    fields = ('sms_id', 'sender_msisdn', 'recipient_msisdn', 'created_at')
    model = PleaseCallMe
    
    @permission_required('gateway.can_view_pcm_statistics')
    @throttle(10, 60)
    def read(self, request):
        if 'since' in request.GET:
            since = iso8601.parse_date(request.GET['since'])
            return PleaseCallMe.objects.filter(created_at__gte=since)
        else:
            return rc.BAD_REQUEST
    
    @permission_required('gateway.can_place_pcm')
    @require_mime('json')
    def create(self, request):
        """
        Receive a please call me message from somewhere, probably FrontlineSMS
        My current FrontlineSMS setup is configured to perform an HTTP request
        triggered by a keyword.

        This is the current URL being requested:

        http://localhost:8000/sms/pcm/? \
                &sender_msisdn=${sender_number} \       # where the PCM came from
                &message_content=${message_content} \   # the original PCM message
                &sms_id=${sms_id} \                     # the SMSC's ID - mb we can use this to avoid duplicates
                &recipient_msisdn=${recipient_number}   # the number the PCM was called to, perhaps we can use this to identify the clinic

        See http://frontlinesms.ning.com/profiles/blog/show?id=2052630:BlogPost:9729 
        for available substitution variables.

        """
        if request.content_type:
            sms_id = request.data.get('sms_id')
            sender_msisdn = request.data.get('sender_msisdn')
            recipient_msisdn = request.data.get('recipient_msisdn')
            message = request.data.get('message', '')
            
            pcm = PleaseCallMe.objects.create(sms_id=sms_id, sender_msisdn=sender_msisdn, 
                                                recipient_msisdn=recipient_msisdn, 
                                                message=message)
            return rc.CREATED
        return rc.BAD_REQUEST
            