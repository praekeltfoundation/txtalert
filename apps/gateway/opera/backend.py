from xmlrpclib import ServerProxy
from ..opera.models import SendSMS
from datetime import datetime, timedelta
from django.utils import simplejson

class Gateway(object):
    """Gateway for communicating with the Opera"""
    def __init__(self, url, service_id, password, channel, verbose=False):
        self.proxy = ServerProxy(url, verbose=verbose)
        self.default_values = {
            'Service': service_id,
            'Password': password, 
            'Channel': channel,
        }
    
    def send_sms(self, numbers, smstexts, delivery=None, expiry=None, \
                        priority='standard', receipt='Y'):
        """Send a bulk of smses SMS"""
        
        struct = self.default_values.copy()
        delivery = delivery or datetime.now()
        expiry = expiry or (delivery + timedelta(days=1))
        
        struct['Numbers'] = ','.join(map(str, numbers))
        struct['SMSTexts'] = smstexts
        struct['Delivery'] = delivery
        struct['Expiry'] = expiry
        struct['Priority'] = priority
        struct['Receipt'] = receipt
        
        proxy_response = self.proxy.EAPIGateway.SendSMS(struct)
        
        send_sms_ids = [SendSMS.objects.create(number=number, \
                                        smstext=smstext, \
                                        delivery=struct['Delivery'], \
                                        expiry=struct['Expiry'], \
                                        priority=struct['Priority'], \
                                        receipt=struct['Receipt'], \
                                        identifier=proxy_response['Identifier']).pk
            for (number, smstext) in zip(numbers, smstexts)]
        # Return a Django QuerySet instead of a list of Django objects
        # allowing us to chain the QS later on
        return SendSMS.objects.filter(pk__in=send_sms_ids)
    def status_for(self, identifier):
        return SendSMS.objects.filter(identifier=identifier)
    


try:
    from mobile.sms.models import OperaGateway
    og = OperaGateway.objects.all()[0]
    gateway = Gateway(og.url, og.service, og.password, og.channel, verbose=True)
except:
    pass
