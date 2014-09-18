from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission
from django.db.models.signals import post_save
from django.utils import timezone

from txtalert.apps.gateway.models import PleaseCallMe, SendSMS

import base64
import json


def basic_auth_string(username, password):
    """
    Encode a username and password for use in an HTTP Basic Authentication
    header
    """
    b64 = base64.encodestring('%s:%s' % (username, password)).strip()
    return 'Basic %s' % b64


def add_perms_to_user(username, permission):
    """
    Helper function to get a user and add permissions to it
    """
    user = User.objects.get(username=username)
    return user.user_permissions.add(
        Permission.objects.get(codename=permission))


class PcmAutomationTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='user', email='user@domain.com', password='password')
        self.user.save()

        # we don't want to be bogged down with signal receivers in this test
        self.original_post_save_receivers = post_save.receivers
        post_save.receivers = []

    def tearDown(self):
        # restore signals
        post_save.receivers = self.original_post_save_receivers

    def test_pcm_receiving(self):
        """We're assuming that FrontlineSMS or some other SMS receiving
        app is correctly programmed to receive SMSs and post them to our
        web end point. We're only testing from that point on.
        """
        add_perms_to_user('user', 'can_place_pcm')

        parameters = {
            'sender_msisdn': '27123456789',
            'recipient_msisdn': '27123456780',
            'sms_id': 'doesntmatteratm',
            # not actual text
            'message': 'Please Call: Test User at 27123456789'
        }

        response = self.client.post(
            '%s?username=%s' % (reverse('api-pcm'), self.user.username),
            parameters,
            HTTP_AUTHORIZATION=basic_auth_string('user', 'password')
        )
        self.assertEquals(response.status_code, 201)  # Created

        pcm = PleaseCallMe.objects.latest('created_at')

        for key, value in parameters.items():
            self.assertEquals(getattr(pcm, key), value)

    def test_pcm_receiving_bad_request(self):
        add_perms_to_user('user', 'can_place_pcm')

        parameters = {
            # no parameters, should raise an error
        }

        response = self.client.post(
            '%s?username=%s' % (reverse('api-pcm'), self.user.username),
            parameters,
            HTTP_AUTHORIZATION=basic_auth_string('user','password')
        )

        self.assertEquals(response.status_code, 400) # Bad Request

    def test_vumi_message_submissions(self):
        add_perms_to_user('user', 'can_place_pcm')
        response = self.client.post(
            '%s?username=%s' % (reverse('api-pcm'), self.user.username),
            json.dumps({
                "message_id": "1",
                "to_addr": "271234560",
                "from_addr": "271234570",
                "content": "Please Call: Test User at 27123456789",
                "transport_name": "sms_transport",
                "transport_type": "sms",
                "transport_metadata": {
                }
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=basic_auth_string('user','password'))

        pcm = PleaseCallMe.objects.latest('created_at')
        self.assertEqual(pcm.sms_id, "1")
        self.assertEqual(pcm.sender_msisdn, "271234570")
        self.assertEqual(pcm.recipient_msisdn, "271234560")
        self.assertEqual(pcm.message, "Please Call: Test User at 27123456789")


class TestEventHandling(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='user', email='user@domain.com', password='password')
        self.sms = SendSMS.objects.create(
            msisdn='27123456789',
            smstext='smstext',
            delivery=timezone.now(),
            expiry=timezone.now(),
            priority='Standard',
            receipt='Y',
            identifier='12345678',
            user=self.user,
        )

    def test_ack(self):
        ack = {
            "event_type": "ack",
            "user_message_id": self.sms.identifier,
        }
        resp = self.client.post(
            reverse('api-events'),
            data=json.dumps(ack),
            content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        sms = SendSMS.objects.get(pk=self.sms.pk)
        self.assertEqual(sms.status, 'd')

    def test_nack(self):
        ack = {
            "event_type": "nack",
            "user_message_id": self.sms.identifier,
        }

        resp = self.client.post(
            reverse('api-events'),
            data=json.dumps(ack),
            content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        sms = SendSMS.objects.get(pk=self.sms.pk)
        self.assertEqual(sms.status, 'F')

    def test_dr_delivered(self):
        ack = {
            "event_type": "delivery_report",
            "delivery_status": "delivered",
            "user_message_id": self.sms.identifier,
        }

        resp = self.client.post(
            reverse('api-events'),
            data=json.dumps(ack),
            content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        sms = SendSMS.objects.get(pk=self.sms.pk)
        self.assertEqual(sms.status, 'D')

    def test_dr_pending(self):
        ack = {
            "event_type": "delivery_report",
            "delivery_status": "pending",
            "user_message_id": self.sms.identifier,
        }

        resp = self.client.post(
            reverse('api-events'),
            data=json.dumps(ack),
            content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        sms = SendSMS.objects.get(pk=self.sms.pk)
        self.assertEqual(sms.status, 'd')

    def test_dr_failed(self):
        ack = {
            "event_type": "delivery_report",
            "delivery_status": "failed",
            "user_message_id": self.sms.identifier,
        }

        resp = self.client.post(
            reverse('api-events'),
            data=json.dumps(ack),
            content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        sms = SendSMS.objects.get(pk=self.sms.pk)
        self.assertEqual(sms.status, 'F')

    def test_dr_unknown(self):
        ack = {
            "event_type": "delivery_report",
            "delivery_status": "foo",
            "user_message_id": self.sms.identifier,
        }

        resp = self.client.post(
            reverse('api-events'),
            data=json.dumps(ack),
            content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        sms = SendSMS.objects.get(pk=self.sms.pk)
        self.assertEqual(sms.status, 'v')

    def test_unknown_user_message_id(self):
        ack = {
            "event_type": "delivery_report",
            "delivery_status": "foo",
        }

        resp = self.client.post(
            reverse('api-events'),
            data=json.dumps(ack),
            content_type='application/json')
        self.assertEqual(resp.status_code, 400)