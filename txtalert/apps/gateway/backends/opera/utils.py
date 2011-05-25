from django.http import HttpResponseBadRequest

from collections import namedtuple
from datetime import datetime
import xml.etree.ElementTree as ET

from txtalert.apps.gateway.models import SendSMS
import iso8601
import logging

OPERA_TIMESTAMP_FORMAT = "%Y%m%dT%H:%M:%S"

def process_receipts_xml(receipt_xml_data):
    tree = ET.fromstring(receipt_xml_data)
    receipts = map(element_to_namedtuple, tree.findall('receipt'))
    return process_receipts(receipts)
    

def process_receipts(receipts):
    """Deal with the list of receipt objects, find & updated associated SendSMSs 
    or mark them as failed.
    
    Returns a tuple of two lists, successful receipts & failed receipts.
    """
    success, fail = [], []
    for receipt in receipts:
        try:
            # internally we store MSISDNs without a leading plus, strip that
            # from the msisdn
            sms_sent = SendSMS.objects.get(identifier=receipt.reference, \
                                        msisdn=receipt.msisdn.replace("+",""))
            sms_sent.status = receipt.status
            sms_sent.delivery_timestamp = datetime.strptime(receipt.timestamp, \
                                                        OPERA_TIMESTAMP_FORMAT)
            sms_sent.save()
            success.append(receipt)
        except SendSMS.DoesNotExist, error:
            logging.info(error)
            fail.append(receipt)
    return success, fail


def element_to_dict(element):
    """
    Turn an ElementTree element '<data><el>1</el></data>' into {el: 1}. Not recursive!
    
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


