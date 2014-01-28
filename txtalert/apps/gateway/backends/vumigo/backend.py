import json
from datetime import datetime, timedelta

import requests

from django.http import HttpResponse
from django.conf import settings

from txtalert.apps.gateway.models import SendSMS


class Gateway(object):

    api_url = ("http://go.vumi.org/api/v1/go/http_api_nostream/"
               "{conversation_key}/messages.json")

    def __init__(self, account_key, conversation_key, access_token):
        self.account_key = account_key
        self.conversation_key = conversation_key
        self.access_token = access_token

    def send_one_sms(self, user, msisdn, smstext):
        url = self.api_url.format(conversation_key=self.conversation_key)
        response = requests.put(url, data=json.dumps({
            "content": smstext,
            "to_addr": msisdn,
        }), auth=(self.account_key, self.access_token))
        reply = response.json()

        send_sms = SendSMS()
        send_sms.user = user
        send_sms.msisdn = msisdn
        send_sms.smstext = smstext
        send_sms.delivery = datetime.now()
        send_sms.expiry = datetime.now() + timedelta(days=1)
        send_sms.priority = 'standard'
        send_sms.receipt = 'Y'
        send_sms.identifier = reply['message_id']
        send_sms.save()
        return send_sms

    def send_smss(self, user, msisdns, smstexts):
        responses = []
        for msisdn, smstext in zip(msisdns, smstexts):
            send_sms = self.send_one_sms(user, msisdn, smstext)
            responses.append(send_sms.pk)
        return SendSMS.objects.filter(pk__in=responses)

gateway = Gateway(settings.VUMIGO_ACCOUNT_KEY,
                  settings.VUMIGO_CONVERSATION_KEY,
                  settings.VUMIGO_CONVERSATION_ACCESS_TOKEN)


def sms_receipt_handler(request, *args, **kwargs):
    data = json.loads(request.raw_post_data)
    send_smss = SendSMS.objects.filter(identifier=data['user_message_id'])
    send_smss.update(status=data['delivery_status'],
                     delivery_timestamp=data['timestamp'])
    return HttpResponse("ok", status=201)
