from django.http import HttpResponseBadRequest
from collections import namedtuple
from opera.models import SendSMS
from datetime import datetime
import xml.etree.ElementTree as ET

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
            sms_sent = SendSMS.objects.get(identifier=receipt.reference, \
                                                                number=receipt.msisdn)
            sms_sent.status = receipt.status
            sms_sent.delivery_timestamp = datetime.strptime(receipt.timestamp, \
                                                            SendSMS.TIMESTAMP_FORMAT)
            sms_sent.save()
            success.append(receipt)
        except SendSMS.DoesNotExist, error:
            logging.error(error)
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


def require_POST_parameters(*parameters, **kwargs):
    return require_parameters(parameters, method='POST', **kwargs)

def require_GET_parameters(*parameters, **kwargs):
    return require_parameters(parameters, method='GET', **kwargs)

def require_parameters(parameters=[], method='REQUEST', reveal=False):
    """Decorator to ensure we get the required parameters for the view and raise
    an HttpResponseBadRequest if we don't.
    
    @require_parameters(['param1','param2'], method='REQUEST')
    def my_view(request):
        # this code will always have request.REQUEST['param1'] 
        # and request.REQUEST['param1']

    """
    def decorator(decorated_function):
        def new_f(request, *args, **kwargs):
            if all([(p in getattr(request, method)) for p in parameters]):
                return decorated_function(request, *args, **kwargs)
            else:
                msg = "Missing some of the required parameters"
                if reveal:
                    msg += ': %s' % ', '.join(parameters)
                return HttpResponseBadRequest(msg)
        return new_f
    return decorator

