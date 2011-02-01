from django.http import HttpResponse
from django.utils import simplejson
from django.contrib.auth.decorators import permission_required
import logging
from txtalert.apps.gateway.models import SendSMS

from txtalert.core.utils import random_string
from datetime import datetime, timedelta

class Gateway(object):
    """Dummy gateway we used to monkey patch the real RPC gateway so we can write
    our test code against something we control"""
    
    def send_sms(self, *args, **kwargs):
        return self.send_bulk_sms(*args, **kwargs)
    
    def send_one_sms(self, user, msisdn, smstext, delivery=None, expiry=None,
                        priority='standard', receipt='Y'):
        delivery = delivery or datetime.now()
        expiry = expiry or (datetime.now() + timedelta(days=1))
        return SendSMS.objects.create(
                                        user=user, 
                                        msisdn=msisdn, 
                                        smstext=smstext, 
                                        delivery=delivery, 
                                        expiry=expiry, 
                                        priority=priority, 
                                        receipt=receipt, 
                                        identifier=random_string()[:8])
    
    def send_bulk_sms(self, user, msisdns, smstexts, *args, **kwargs):
        return [self.send_one_sms(user, msisdn, smstext, *args, **kwargs)
                            for (msisdn, smstext) in zip(msisdns, smstexts)]


gateway = Gateway()

# no sms receipt handling for dummy gateway
sms_receipt_handler = None
