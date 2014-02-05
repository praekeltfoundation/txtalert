from vumiclient.client import Client
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from txtalert.apps.gateway.models import SendSMS

class Gateway(object):

    def __init__(self, username, password):
        self.client = Client(username, password)

    def send_one_sms(self, user, msisdn, smstext):
        resp = self.client.send_sms(to_msisdn=msisdn, from_msisdn='0',
                    message=smstext).pop()
        send_sms = SendSMS()
        send_sms.user = user
        send_sms.msisdn = msisdn
        send_sms.smstext = smstext
        send_sms.delivery = timezone.now()
        send_sms.expiry = timezone.now() + timedelta(days=1)
        send_sms.priority = 'standard'
        send_sms.receipt = 'Y'
        send_sms.identifier = str(resp.id)
        send_sms.save()
        return send_sms

    def send_sms(self, user, msisdns, smstexts):
        responses = []
        for msisdn, smstext in zip(msisdns, smstexts):
            send_sms = self.send_one_sms(user, msisdn, smstext)
            responses.append(send_sms.pk)
        return SendSMS.objects.filter(pk__in=responses)

gateway = Gateway(settings.VUMI_USERNAME, settings.VUMI_PASSWORD)

def sms_receipt_handler(request, *args, **kwargs):
    send_smss = SendSMS.objects.filter(identifier=request.POST.get('id'))
    send_smss.update(status=request.POST.get('transport_status'),
        delivery_timestamp=request.POST.get('delivered_at'))
    return HttpResponse("ok", status=201)

