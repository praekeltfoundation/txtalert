from xmlrpclib import ServerProxy
from datetime import datetime, timedelta

from django.conf import settings
from txtalert.apps.gateway.models import SendSMS

class Gateway(object):
    """Gateway for communicating with the Opera"""
    def __init__(self, url, service_id, password, channel, verbose=False):
        self.proxy = ServerProxy(url, verbose=verbose)
        self.default_values = {
            'Service': service_id,
            'Password': password, 
            'Channel': channel,
        }
    
    def send_sms(self, user, msisdns, smstexts, delivery=None, expiry=None, \
                     priority='standard', receipt='Y'):
        """Deprecated, replaced with send_bulk_sms"""
        send_sms_ids = [self.send_one_sms(user, msisdn, smstext, delivery, 
                                    expiry, priority, receipt).pk \
                    for (msisdn, smstext) in zip(msisdns, smstexts)]
        return SendSMS.objects.filter(pk__in=send_sms_ids)
        
    
    def send_one_sms(self, user, msisdn, smstext, delivery=None, expiry=None, \
                        priority='standard', receipt='Y'):
        """Send one sms"""
        struct = self.default_values.copy()
        delivery = delivery or datetime.utcnow()
        expiry = expiry or (delivery + timedelta(days=1))
        
        struct['Numbers'] = msisdn
        struct['SMSText'] = smstext
        struct['Delivery'] = delivery
        struct['Expiry'] = expiry
        struct['Priority'] = priority
        struct['Receipt'] = receipt
        
        proxy_response = self.proxy.EAPIGateway.SendSMS(struct)
        
        return SendSMS.objects.create(user=user,
                                        msisdn=msisdn,
                                        smstext=smstext, 
                                        delivery=struct['Delivery'], 
                                        expiry=struct['Expiry'], 
                                        priority=struct['Priority'], 
                                        receipt=struct['Receipt'], 
                                        identifier=proxy_response['Identifier'])
    
    def send_bulk_sms(self, user, msisdns, smstexts, delivery=None, expiry=None, \
                        priority='standard', receipt='Y'):
        """Send a bulk of smses SMS"""
        
        struct = self.default_values.copy()
        delivery = delivery or datetime.utcnow()
        expiry = expiry or (delivery + timedelta(days=1))
        
        struct['Numbers'] = ','.join(map(str, msisdns))
        struct['SMSTexts'] = smstexts
        struct['Delivery'] = delivery
        struct['Expiry'] = expiry
        struct['Priority'] = priority
        struct['Receipt'] = receipt
        
        proxy_response = self.proxy.EAPIGateway.SendSMS(struct)
        
        send_sms_ids = [SendSMS.objects.create(
                                        user=user,
                                        msisdn=msisdn, 
                                        smstext=smstext, 
                                        delivery=struct['Delivery'], 
                                        expiry=struct['Expiry'], 
                                        priority=struct['Priority'], 
                                        receipt=struct['Receipt'], 
                                        identifier=proxy_response['Identifier']).pk
            for (msisdn, smstext) in zip(msisdns, smstexts)]
        
        # FIXME: probably silly optimization which'll hurt in the long run
        # Return a Django QuerySet instead of a list of Django objects
        # allowing us to chain the QS later on
        return SendSMS.objects.filter(pk__in=send_sms_ids)


# FIXME, this is hideous
gateway = Gateway('https://dragon.sa.operatelecom.com:1089/Gateway', 
                    settings.OPERA_SERVICE, 
                    settings.OPERA_PASSWORD, 
                    settings.OPERA_CHANNEL, 
                    verbose=settings.DEBUG)

from views import sms_receipt_handler

