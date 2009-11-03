from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseNotFound
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
import xml.etree.ElementTree as ET
from opera.gateway import gateway
from opera.models import SendSMS
from opera.utils import element_to_namedtuple
from opera.resource import SendSMSResource
from opera.auth import has_perm_or_basicauth
from datetime import datetime, timedelta
import logging


def process_receipts(receipts):
    """Deal with the list of receipt objects, find & updated associated SendSMSs 
    or mark them as failed.
    
    Returns a tuple of two lists, successful receipts & failed receipts.
    """
    success, fail = [], []
    for receipt in receipts:
        try:
            sms_sent = SendSMS.objects.get(identifier=receipt.reference, \
                                                                number=receipt.msisdn)
            sms_sent.status = receipt.status
            sms_sent.delivery_timestamp = datetime.strptime(receipt.timestamp, \
                                                            SendSMS.TIMESTAMP_FORMAT)
            sms_sent.save()
            success.append(receipt._asdict())
        except SendSMS.DoesNotExist, error:
            logging.error(error)
            fail.append(receipt._asdict())
    return success, fail


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
    tree = ET.fromstring(request.raw_post_data)
    receipts = map(element_to_namedtuple, tree.findall('receipt'))
    success, fail = process_receipts(receipts)
    return HttpResponse(simplejson.dumps({
        'success': success,
        'fail': fail
    }), content_type='text/json')


@require_POST
@has_perm_or_basicauth('opera.can_send_sms')
def send(request, format):
    sent_smss = gateway.send_sms(request.POST.getlist('numbers'),request.POST.getlist('smstexts'))
    return HttpResponse(SendSMSResource(sent_smss).publish('json'), \
                        content_type='text/json')

@require_GET
@has_perm_or_basicauth('opera.can_view_statistics')
def statistics(request, format):
    """Present SendSMS statistics over an HTTP API. Unless the since parameter
    is provided assume we want the data for this day.
    """
    since = request.GET.get('since', None)
    if since:
        since = datetime.strptime(since, SendSMS.TIMESTAMP_FORMAT)
    else:
        since = datetime.now() - timedelta(days=1)
    sent_smss = SendSMS.objects.filter(delivery__gte=since)
    return HttpResponse(SendSMSResource(sent_smss).publish(format), \
                                        content_type='text/%s' % format)