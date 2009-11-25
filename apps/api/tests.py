from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import simplejson
from django.db.models.signals import post_save

from gateway.backends.opera.utils import element_to_namedtuple, OPERA_TIMESTAMP_FORMAT
from gateway.backends.opera.backend import gateway
from gateway.models import SendSMS, PleaseCallMe

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import base64
import iso8601

def basic_auth_string(username, password):
    """
    Encode a username and password for use in an HTTP Basic Authentication
    header
    """
    b64 = base64.encodestring('%s:%s' % (username, password)).strip()
    return 'Basic %s' % b64


def add_perms_to_user(username, permission): # perms as in permissions, not the hair
    """
    Helper function to get a user and add permissions to it
    """
    user = User.objects.get(username=username)
    return user.user_permissions.add(Permission.objects.get(codename=permission))


class MockGateway(object):
    """Dummy gateway we used to monkey patch the real RPC gateway so we can write
    our test code against something we control"""
    
    def use_identifier(self, identifier):
        """specify what identifier to return"""
        self.identifier = identifier
    
    def SendSMS(self, args):
        return {'Identifier': self.identifier}
    


class JSONTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
    
    def json_get(self, *args, **kwargs):
        return self.json_request('get', *args, **kwargs)
    
    def json_post(self, *args, **kwargs):
        return self.json_request('post', *args, **kwargs)
    
    def json_put(self, *args, **kwargs):
        return self.json_request('put', *args, **kwargs)
    
    def json_delete(self, *args, **kwargs):
        return self.json_request('delete', *args, **kwargs)
    
    def json_request(self, method, path, parameters = {}, content_type='application/json', auth=basic_auth_string('user','password')):
        path = reverse(path, kwargs={'emitter_format': 'json'})
        meth = getattr(self.client, method)
        return meth(
                path,
                parameters,
                content_type=content_type,
                HTTP_AUTHORIZATION=auth
        )

class OperaTestCase(JSONTestCase):
    """Testing the opera gateway interactions"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='user', \
                                                email='user@domain.com', \
                                                password='password')
        self.user.save()
        
        # specify the proxy's EAPIGateway, which is what Opera uses internally
        setattr(gateway.proxy, 'EAPIGateway', MockGateway())
        
        # add a helper function to set the identifier
        def use_identifier(identifier):
            gateway.proxy.EAPIGateway.use_identifier(identifier)
        setattr(gateway, 'use_identifier', use_identifier)
    
    def test_send_sms(self):
        """we've hijacked the EAPIGateway and tell it what to return as the 
        identifier. The SendSMS object should store that identifier after 
        communicating with the RPC gateway"""
        gateway.use_identifier('12345678')
        [send_sms,] = gateway.send_sms(['27764493806'],['testing'])
        self.assertEqual(send_sms.identifier, '12345678')
    
    def test_receipt_processing(self):
        """Test the receipt XML we get back from Opera when a message has been 
        sent successfully"""
        raw_xml_post = """
        <?xml version="1.0"?>
        <!DOCTYPE receipts>
        <receipts>
          <receipt>
            <msgid>26567958</msgid>
            <reference>001efc31</reference>
            <msisdn>+44727204592</msisdn>
            <status>D</status>
            <timestamp>20080831T15:59:24</timestamp>
            <billed>NO</billed>
          </receipt>
          <receipt>
            <msgid>26750677</msgid>
            <reference>001f4041</reference>
            <msisdn>+44733476814</msisdn>
            <status>D</status>
            <timestamp>20080907T09:42:28</timestamp>
            <billed>NO</billed>
          </receipt>
        </receipts>
        """
        
        # fake us having sent SMSs and having stored the proper identifiers
        tree = ET.fromstring(raw_xml_post.strip())
        receipts = map(element_to_namedtuple, tree.findall('receipt'))
        
        for receipt in receipts:
            gateway.use_identifier(receipt.reference)
            gateway.send_sms([receipt.msisdn], ['testing %s' % receipt.reference])
        
        # mimick POSTed receipt from Opera
        add_perms_to_user('user','can_place_sms_receipt')
        response = self.client.post(reverse('api-sms-receipt',kwargs={'emitter_format':'json'}), raw_xml_post.strip(), \
                                    content_type='text/xml', HTTP_AUTHORIZATION=basic_auth_string('user','password'))
        
        # it should return a JSON response
        self.assertEquals(response['Content-Type'], 'application/json; charset=utf-8')
        
        # test the json response
        from django.utils import simplejson
        data = simplejson.loads(response.content)
        self.assertTrue(data.keys(), ['fail','success'])
        # all should've succeeded
        self.assertEquals(len(data['success']), 2)
        # we should get the dict back representing the receipt
        self.assertEquals([r._asdict() for r in receipts], data['success'])
        
        # check database state
        for receipt in receipts:
            send_sms = SendSMS.objects.get(msisdn=receipt.msisdn, identifier=receipt.reference)
            self.assertEquals(send_sms.delivery_timestamp, datetime.strptime(receipt.timestamp, OPERA_TIMESTAMP_FORMAT))
            self.assertEquals(send_sms.status, 'D')
    
    def test_json_sms_statistics_auth(self):
        response = self.json_get(path='api-sms', auth=basic_auth_string('invalid','user'))
        self.assertEquals(response.status_code, 401) # Http Basic Auth
        
        add_perms_to_user('user', 'can_view_sms_statistics')
        
        response = self.json_get(path='api-sms', parameters={
            "since": datetime.now().strftime(SendSMS.TIMESTAMP_FORMAT)
        })
        
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/json; charset=utf-8')
    
    def test_send_sms_json_response(self):
        add_perms_to_user('user', 'can_send_sms')
        gateway.use_identifier('a' * 8)
        response = self.client.post(reverse('api-sms',kwargs={'emitter_format':'json'}), simplejson.dumps({
                'msisdns': ['27123456789'],
                'smstext': 'hello'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=basic_auth_string('user','password'))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/json; charset=utf-8')
        
        data = simplejson.loads(response.content)
        self.assertTrue(len(data),1)
        receipt = data[0]
        self.assertEquals(receipt['identifier'], 'a' * 8)
    
    def test_send_multiple_sms_response(self):
        add_perms_to_user('user', 'can_send_sms')
        gateway.use_identifier('b' * 8)
        response = self.client.post(reverse('api-sms',kwargs={'emitter_format':'json'}), simplejson.dumps({
            'msisdns': ['27123456789', '27123456781'],
            'smstext': 'bla bla bla'
            }),
            content_type = 'application/json',
            HTTP_AUTHORIZATION=basic_auth_string('user','password'))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/json; charset=utf-8')
        
        data = simplejson.loads(response.content)
        self.assertTrue(len(data),2)
        for receipt in data:
            self.assertEquals(receipt['identifier'], 'b' * 8)
    
    def test_send_too_large_sms(self):
        add_perms_to_user('user', 'can_send_sms')
        gateway.use_identifier('c' * 8)
        
        response = self.client.post(reverse('api-sms',kwargs={'emitter_format':'json'}), simplejson.dumps({
                'msisdns': ['27123456789'],
                'smstext': 'a' * 161 # 1 char too large
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=basic_auth_string('user','password'))
        self.assertEquals(response.status_code, 400) # HttpResponseBadRequest
    

class PcmAutomationTestCase(JSONTestCase):
    
    fixtures = ['contacts.json']
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user', \
                                                email='user@domain.com', \
                                                password='password')
        self.user.save()
        
        # we don't want to be bogged down with signal receivers in this test
        self.original_post_save_receivers = post_save.receivers
        post_save.receivers = []
    
    def tearDown(self):
        # restore signals
        post_save.receivers = self.original_post_save_receivers
    
    def test_pcm_receiving(self):
        """We're assuming that FrontlineSMS or some other SMS receiving app
        is correctly programmed to receive SMSs and post them to our web end point.
        We're only testing from that point on.
        """
        add_perms_to_user('user', 'can_place_pcm')
        
        parameters = {
            'sender_msisdn': '27123456789',
            'recipient_msisdn': '27123456780',
            'sms_id': 'doesntmatteratm',
            'message': 'Please Call: Test User at 27123456789' # not actual text
        }
        
        response = self.client.post(reverse('api-pcm',kwargs={'emitter_format':'json'}),
            parameters,
            HTTP_AUTHORIZATION=basic_auth_string('user','password')
        )
        
        self.assertEquals(response.status_code, 201) # Created
        
        pcm = PleaseCallMe.objects.latest('created_at')
        
        for key, value in parameters.items():
            self.assertEquals(getattr(pcm, key), value)
    
    def test_pcm_statistics(self):
        response = self.json_get(path='api-pcm', auth=basic_auth_string('invalid', 'user'))
        self.assertEquals(response.status_code, 401) # Http Basic Auth
        
        add_perms_to_user('user', 'can_place_pcm')
        add_perms_to_user('user', 'can_view_pcm_statistics')
        
        # place a PCM
        parameters = {
            'sender_msisdn': '27123456789',
            'recipient_msisdn': '27123456780',
            'sms_id': 'doesntmatteratm',
            'message': 'Please Call: Test User at 27123456789' # not actual text
        }
        
        response = self.client.post(reverse('api-pcm',kwargs={'emitter_format':'json'}), 
                        parameters,
                        HTTP_AUTHORIZATION=basic_auth_string('user','password')
                    )
        
        # fetch it via the API
        yesterday = datetime.now() - timedelta(days=1)
        response = self.json_get(path='api-pcm', parameters={
            "since": yesterday.strftime(SendSMS.TIMESTAMP_FORMAT)
        })
        
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/json; charset=utf-8')
        from django.utils import simplejson
        data = simplejson.loads(response.content)
        self.assertTrue(len(data) == 1)
        first_item = data[0]
        
        from api.handlers import PCMHandler
        
        # test the fields exposed by the PCMHandler
        for key in ('sms_id', 'sender_msisdn', 'recipient_msisdn'):
            self.assertEquals(parameters[key], first_item[key])
        