from django.test import TestCase
from txtalert.apps.gateway.backends.dummy import backend
from txtalert.apps import gateway
from txtalert.apps.gateway.models import *
from datetime import datetime

class GatewayLoadingTestCase(TestCase):
    
    def test_loading_of_dummy_gateway(self):
        # load dummy
        gateway.load_backend('txtalert.apps.gateway.backends.dummy')
        # make sure it's been loaded
        self.assertTrue(isinstance(gateway.gateway, backend.Gateway))
    
    def test_load_of_bad_gateway(self):
        self.assertRaises(
            gateway.GatewayException,
            gateway.load_backend,
            'gateway.does.not.exist'
        )


class GatewayModelTestCase(TestCase):
    
    def test_send_sms_unicode(self):
        sms = SendSMS(
            msisdn='27123456789',
            smstext='',
            delivery=datetime.now(),
            expiry=datetime.now(),
            priority='Standard',
            receipt='Y',
            identifier='identifier'
        )
        self.assertEquals(
            u'SendSMS: identifier - 27123456789',
            unicode(sms)
        )
    
    def test_pcm_unicode(self):
        pcm = PleaseCallMe(
            sms_id='sms_id',
            sender_msisdn='27123456789',
            recipient_msisdn='27123456780',
        )
        self.assertEquals(
            u'PleaseCallMe: 27123456789',
            unicode(pcm)
        )
    