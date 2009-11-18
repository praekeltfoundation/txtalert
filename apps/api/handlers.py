from django.contrib.auth.decorators import permission_required
from django.utils import simplejson
from django.http import HttpResponse

from piston.handler import BaseHandler
from piston.utils import rc, require_mime

from opera.utils import require_POST_parameters, require_GET_parameters, process_receipts_xml
from opera.models import SendSMS, PleaseCallMe
from opera.gateway import gateway

from datetime import datetime
import logging

class SMSHandler(BaseHandler):
    allowed_methods = ('POST', 'GET')
    fields = ('identifier', 'delivery', 'expiry', 'delivery_timestamp', 
                'status', 'status_display', 'number')
    model = SendSMS
    
    @permission_required('opera.can_view_sms_statistics')
    def read(self, request):
        base = SendSMS.objects
        if 'number' in request.GET and 'identifier' in request.GET:
            number = request.GET.get('number')
            identifier = request.GET.get('identifier')
            return base.get(number=number, identifier=identifier)
        else:
            since = datetime.strptime(request.GET['since'], SendSMS.TIMESTAMP_FORMAT)
            return base.filter(delivery__gte=since)
    
    @permission_required('opera.can_send_sms')
    @require_mime('json')
    def create(self, request):
        if request.content_type:
            numbers = request.data['numbers']
            smstext = request.data['smstext']
            if len(smstext) <= 160:
                return gateway.send_sms(numbers, (smstext,) * len(numbers))
        return rc.BAD_REQUEST


class SMSReceiptHandler(BaseHandler):
    allowed_methods = ('POST')
    
    @permission_required('opera.can_place_sms_receipt')
    @require_mime('xml')
    def create(self, request):
        logging.debug(request.raw_post_data)
        success, fail = process_receipts_xml(request.raw_post_data)
        return HttpResponse(simplejson.dumps({
            'success': map(lambda rcpt: rcpt._asdict(), success),
            'fail': map(lambda rcpt: rcpt._asdict(), fail)
        }), status=201, content_type='application/json; charset=utf-8')
    

class PCMHandler(BaseHandler):
    allowed_methods = ('POST', 'GET')
    fields = ('sms_id', 'sender_number', 'recipient_number', 'created_at')
    model = PleaseCallMe
    
    def read(self, request):
        since = datetime.strptime(request.GET['since'], SendSMS.TIMESTAMP_FORMAT)
        return PleaseCallMe.objects.filter(created_at__gte=since)
    
    @permission_required('opera.can_place_pcm')
    @require_mime('json')
    def create(self, request):
        """
        Receive a please call me message from somewhere, probably FrontlineSMS
        My current FrontlineSMS setup is configured to perform an HTTP request
        triggered by a keyword.

        This is the current URL being requested:

        http://localhost:8000/sms/pcm/? \
                &sender_number=${sender_number} \       # where the PCM came from
                &message_content=${message_content} \   # the original PCM message
                &sms_id=${sms_id} \                     # the SMSC's ID - mb we can use this to avoid duplicates
                &recipient_number=${recipient_number}   # the number the PCM was called to, perhaps we can use this to identify the clinic

        See http://frontlinesms.ning.com/profiles/blog/show?id=2052630:BlogPost:9729 
        for available substitution variables.

        """
        if request.content_type:
            sms_id = request.data.get('sms_id')
            sender_number = request.data.get('sender_number')
            recipient_number = request.data.get('recipient_number')
            message = request.data.get('message', '')
            
            pcm = PleaseCallMe.objects.create(sms_id=sms_id, sender_number=sender_number, 
                                                recipient_number=recipient_number, 
                                                message=message)
            return rc.CREATED
        return rc.BAD_REQUEST
            