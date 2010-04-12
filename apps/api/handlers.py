from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404

from piston.handler import BaseHandler
from piston.utils import rc, require_mime, throttle

from gateway.models import SendSMS, PleaseCallMe
from gateway import gateway, sms_receipt_handler

from datetime import datetime
import logging
import iso8601

class SMSHandler(BaseHandler):
    allowed_methods = ('POST', 'GET')
    fields = ('identifier', 'delivery', 'expiry', 'delivery_timestamp', 
                'status', 'status_display', 'msisdn')
    model = SendSMS
    
    # FIXME: the way I deal with one resource & a list of resource in one view
    # is hideous
    @permission_required('gateway.can_view_sms_statistics')
    @throttle(10, 60)
    def read(self, request, msisdn=None, identifier=None):
        if all([msisdn, identifier]):
            return get_object_or_404(SendSMS, msisdn=msisdn, identifier=identifier)
        else:
            return self._read_list(request)
    
    def _read_list(self, request):
        if 'since' in request.GET:
            # remove timezone info since MySQL is not able to handle that
            # assume input it UTC
            since = iso8601.parse_date(request.GET['since']).replace(tzinfo=None)
            return SendSMS.objects.filter(delivery__gte=since)
        else:
            return rc.BAD_REQUEST
    
    
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
    """This is completely handed off to the specified gateway, it should
    specify the sms_receipt_handler, this can be a regular Django view 
    responding some type of HttpResponse object"""
    allowed_methods = ('POST',)
    create = sms_receipt_handler

class PCMHandler(BaseHandler):
    allowed_methods = ('POST', 'GET')
    fields = ('sms_id', 'sender_msisdn', 'recipient_msisdn', 'created_at')
    model = PleaseCallMe
    
    @permission_required('gateway.can_view_pcm_statistics')
    @throttle(10, 60)
    def read(self, request):
        """
        Return the list of PleaseCallMe's received since the timestamp specified 
        in the `since` parameter.
        """
        if 'since' in request.GET:
            # remove timezone info since MySQL is not able to handle that
            # assume input it UTC
            since = iso8601.parse_date(request.GET['since']).replace(tzinfo=None)
            return PleaseCallMe.objects.filter(created_at__gte=since)
        else:
            return rc.BAD_REQUEST
    
    @permission_required('gateway.can_place_pcm')
    def create(self, request):
        """
        FIXME: This should probably be moved into something more pluggable, it 
                shouldn't rely on FrontlineSMS. FrontlineSMS should be one of 
                several options
        
        Receive a please call me message from somewhere, probably FrontlineSMS
        My current FrontlineSMS setup is configured to perform an HTTP request
        triggered by a keyword.
        
        This is the current URL being requested:
        
        http://localhost:8000/api/v1/pcm.json? \
                &sender_msisdn=${sender_number} \       # where the PCM came from
                &message_content=${message_content} \   # the original PCM message
                &sms_id=${sms_id} \                     # the SMSC's ID - mb we can use this to avoid duplicates
                &recipient_msisdn=${recipient_number}   # the number the PCM was called to, perhaps we can use this to identify the clinic
        
        See http://frontlinesms.ning.com/profiles/blog/show?id=2052630:BlogPost:9729 
        for available substitution variables.
        
        """
        
        if ('sms_id' in request.POST
            and 'sender_msisdn' in request.POST 
            and 'recipient_msisdn' in request.POST):
            sms_id = request.POST.get('sms_id')
            sender_msisdn = request.POST.get('sender_msisdn')
            recipient_msisdn = request.POST.get('recipient_msisdn')
            message = request.POST.get('message', '')
            
            pcm = PleaseCallMe.objects.create(sms_id=sms_id, sender_msisdn=sender_msisdn, 
                                                recipient_msisdn=recipient_msisdn, 
                                                message=message)
            resp = rc.CREATED
            resp.content = 'Please Call Me registered'
            return resp
        return rc.BAD_REQUEST
    
