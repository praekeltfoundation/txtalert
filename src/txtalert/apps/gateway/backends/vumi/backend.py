from vumiclient.client import Client
from datetime import datetime, timedelta
from django.conf import settings
from txtalert.apps.gateway.models import SendSMS

class Gateway(object):
    
    def __init__(self, username, password):
        self.client = Client(username, password)

    def send_sms(self, user, msisdns, smstexts):
        responses = []
        for msisdn, smstext in zip(msisdns, smstexts):
            resp = self.client.send_sms(to_msisdn=msisdn, from_msisdn='0',
                    message=smstext).pop()
            send_sms = SendSMS()
            send_sms.user = user
            send_sms.msisdn = msisdn
            send_sms.smstext = smstext
            send_sms.delivery = datetime.now()
            send_sms.expiry = datetime.now() + timedelta(days=1)
            send_sms.priority = 'standard'
            send_sms.receipt = 'Y'
            send_sms.identifier = str(resp.id)
            send_sms.save()

            responses.append(send_sms.pk)
        return SendSMS.objects.filter(pk__in=responses)

gateway = Gateway(settings.VUMI_USERNAME, settings.VUMI_PASSWORD)

def sms_receipt_handler(request, *args, **kwargs):
    print request, args, kwargs
