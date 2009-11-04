from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.utils import simplejson
from django.views.decorators.http import require_POST, require_GET
from opera.gateway import gateway
from opera.models import SendSMS
from opera.utils import (process_receipts_xml, require_POST_parameters, 
                            require_GET_parameters)
from opera.resource import SendSMSResource
from opera.auth import has_perm_or_basicauth
from datetime import datetime, timedelta
import logging

@require_POST
def receipt(request):
    """Process a POSTed XML receipt from Opera, this is what it looks like:
    
        <?xml version="1.0"?>
        <!DOCTYPE receipts>
        <receipts>
          <receipt>
            <msgid>26567958</msgid>
            <reference>001efc31</reference>
            <msisdn>+44727204592</msisdn>
            <status>D</status>
            <timestamp>20080831T15:59:24</timestamp>
            <billed>NO</billed>
          </receipt>
          <receipt>
            <msgid>26750677</msgid>
            <reference>001f4041</reference>
            <msisdn>+44733476814</msisdn>
            <status>D</status>
            <timestamp>20080907T09:42:28</timestamp>
            <billed>NO</billed>
          </receipt>
        </receipts>
    
    """
    logging.debug(request.raw_post_data)
    success, fail = process_receipts_xml(request.raw_post_data)
    return HttpResponse(simplejson.dumps({
        'success': map(lambda rcpt: rcpt._asdict(), success),
        'fail': map(lambda rcpt: rcpt._asdict(), fail)
    }), content_type='text/json')


@has_perm_or_basicauth('opera.can_send_sms')
@require_POST
@require_POST_parameters('number','smstext')
def send(request, format):
    numbers = request.POST.getlist('number')
    smstext = request.POST.get('smstext')
    sent_smss = gateway.send_sms(numbers, (smstext,) * len(numbers))
    return HttpResponse(SendSMSResource(sent_smss).publish(format), \
                                                content_type='text/%s' % format)

@has_perm_or_basicauth('opera.can_view_statistics')
@require_GET
@require_GET_parameters('since', reveal=True)
def statistics(request, format):
    """Present SendSMS statistics over an HTTP API. Unless the since parameter
    is provided assume we want the data for this day.
    """
    since = datetime.strptime(request.GET['since'], SendSMS.TIMESTAMP_FORMAT)
    sent_smss = SendSMS.objects.filter(delivery__gte=since)
    return HttpResponse(SendSMSResource(sent_smss).publish(format), \
                                        content_type='text/%s' % format)