import os
from xmlrpclib import ServerProxy
from datetime import datetime, timedelta

from gateway.models import SendSMS

class Gateway(object):
    """Gateway for communicating with the Opera"""
    def __init__(self, url, service_id, password, channel, verbose=False):
        self.proxy = ServerProxy(url, verbose=verbose)
        self.default_values = {
            'Service': service_id,
            'Password': password, 
            'Channel': channel,
        }
    
    def send_sms(self, msisdns, smstexts, delivery=None, expiry=None, \
                        priority='standard', receipt='Y'):
        """Send a bulk of smses SMS"""
        
        struct = self.default_values.copy()
        delivery = delivery or datetime.now()
        expiry = expiry or (delivery + timedelta(days=1))
        
        struct['Numbers'] = ','.join(map(str, msisdns))
        struct['SMSTexts'] = smstexts
        struct['Delivery'] = delivery
        struct['Expiry'] = expiry
        struct['Priority'] = priority
        struct['Receipt'] = receipt
        
        proxy_response = self.proxy.EAPIGateway.SendSMS(struct)
        
        send_sms_ids = [SendSMS.objects.create(msisdn=msisdn, \
                                        smstext=smstext, \
                                        delivery=struct['Delivery'], \
                                        expiry=struct['Expiry'], \
                                        priority=struct['Priority'], \
                                        receipt=struct['Receipt'], \
                                        identifier=proxy_response['Identifier']).pk
            for (msisdn, smstext) in zip(msisdns, smstexts)]
        
        # FIXME: probably silly optimization which'll hurt in the long run
        # Return a Django QuerySet instead of a list of Django objects
        # allowing us to chain the QS later on
        return SendSMS.objects.filter(pk__in=send_sms_ids)


# FIXME, this is hideous
gateway = Gateway('https://dragon.sa.operatelecom.com:1089/Gateway', 
                    os.environ['OPERA_SERVICE'], 
                    os.environ['OPERA_PASSWORD'], 
                    os.environ['OPERA_CHANNEL'], 
                    verbose=True)

from views import sms_receipt_handler

