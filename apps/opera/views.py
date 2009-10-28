from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseNotFound
from django.utils import simplejson
import xml.etree.ElementTree as ET
from opera.models import SendSMS
from opera.utils import element_to_namedtuple
from datetime import datetime
import logging


def process_receipts(receipts):
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

# Create your views here.
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
    if request.POST:
        logging.debug(request.raw_post_data)
        tree = ET.fromstring(request.raw_post_data)
        receipts = map(element_to_namedtuple, tree.findall('receipt'))
        success, fail = process_receipts(receipts)
        return HttpResponse(simplejson.dumps({
            'success': success,
            'fail': fail
        }), content_type='text/json')
    else:
        return HttpResponseNotAllowed(['POST'])