from django.http import HttpResponse, HttpResponseNotAllowed
from collections import namedtuple
import xml.etree.ElementTree as ET
from opera.models import SendSMS
from datetime import datetime
import logging

def element_to_dict(element):
    """
    turn <data><el>1</el></data> into {el: 1}. Not recursive!
    
    >>> data = ET.fromstring("<data><el>1</el></data>")
    >>> element_to_dict(data)
    {'el': '1'}
    >>>
    
    """
    return dict([(child.tag, child.text) for child in element.getchildren()])

def element_to_namedtuple(element):
    """
    Turn an ElementTree element into an object with named params. Not recursive!
    
    >>> data = ET.fromstring("<data><el>1</el></data>")
    >>> element_to_namedtuple(data)
    data(el='1')
    
    """
    d = element_to_dict(element)
    klass = namedtuple(element.tag, d.keys())
    return klass._make(d.values())

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
        for receipt in map(element_to_namedtuple, tree.findall('receipt')):
            try:
                sms_sent = SendSMS.objects.get(identifier=receipt.reference, \
                                                            number=receipt.msisdn)
                sms_sent.status = receipt.status
                sms_sent.delivery_timestamp = datetime.strptime(receipt.timestamp, \
                                                                SendSMS.TIMESTAMP_FORMAT)
                sms_sent.save()
            except SendSMS.DoesNotExist, error:
                logging.error(error)
    else:
        return HttpResponseNotAllowed('Use POST')