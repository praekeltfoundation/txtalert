from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import simplejson
from django.db.models.signals import post_save
from txtalert.apps.gateway.backends.opera.utils import element_to_namedtuple, OPERA_TIMESTAMP_FORMAT
from txtalert.apps.gateway.models import SendSMS, PleaseCallMe

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import base64
import iso8601
from txtalert.apps import gateway
backend, gateway, receipt_handler = gateway.load_backend('txtalert.apps.gateway.backends.dummy')

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


class OperaTestCase(TestCase):
    """FIXME: This should really be part of the gateway test suite"""
    def setUp(self):
        self.user = User.objects.create_user(username='user', \
                                                email='user@domain.com', \
                                                password='password')
    
    def test_gateway(self):
        # FIXME: this is hideous
        from django.conf import settings
        settings.OPERA_SERVICE = 'dummy'
        settings.OPERA_PASSWORD = 'passwd'
        settings.OPERA_CHANNEL = 'dummy'
        from txtalert.apps.gateway.backends.opera.backend import Gateway
        gateway = Gateway(url="http://testserver/xmlrpc",
                            service_id='dummy_service_id',
                            password='dummy_password',
                            channel='dummy_channel',
                            verbose=True    # putting it on verbose because this 
                                            # gateway should never do any real 
                                            # http calls as part of the test,
                                            # if it is, we'll see it and we'll
                                            # know something is wrong
                        )
        
        class MockedEAPIGateway(object):
            """Mocked XMLRPC interface"""
            def SendSMS(msisdns, smstexts, delivery=None, expiry=None,
                                priority='standard', receipt='Y'):
                return {
                    'Identifier': 'a' * 8
                }
        
        setattr(gateway.proxy, 'EAPIGateway', MockedEAPIGateway())
        sent_smss = gateway.send_sms(self.user,['27123456789'],['testing hello'])
        self.assertEquals(sent_smss.count(), 1)
        self.assertEquals(sent_smss[0].user, self.user)
        self.assertEquals(sent_smss[0].identifier, 'a' * 8)
        self.assertEquals(sent_smss[0].msisdn, '27123456789')
        self.assertEquals(sent_smss[0].smstext, 'testing hello')
        
    
    def test_good_receipt_processing(self):
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
            # FIXME: we need normalization FAST
            [send_sms] = gateway.send_sms(self.user, [receipt.msisdn.replace("+","")], 
                                            ['testing %s' % receipt.reference])
            # manually specifiy the identifier so we can compare it later with the
            # posted receipt
            send_sms.identifier = receipt.reference
            send_sms.save()
        
        # mimick POSTed receipt from Opera
        add_perms_to_user('user','can_place_sms_receipt')
        
        from django.test.client import RequestFactory
        factory = RequestFactory(HTTP_AUTHORIZATION=basic_auth_string('user', 'password'))
        request = factory.post('/', raw_xml_post.strip(), content_type='application/xml; charset=utf-8;')
        request.user = User.objects.get(username='user')
        
        # ugly monkey patching to avoid us having to use a URL to test the opera
        # backend
        from txtalert.apps.gateway.backends.opera.views import sms_receipt_handler
        response = sms_receipt_handler(request)
        
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
            # FIXME: normalization please ...
            send_sms = SendSMS.objects.get(msisdn=receipt.msisdn.replace("+",""), identifier=receipt.reference)
            self.assertEquals(send_sms.delivery_timestamp, datetime.strptime(receipt.timestamp, OPERA_TIMESTAMP_FORMAT))
            self.assertEquals(send_sms.status, 'D')
            self.assertEquals(send_sms.user, self.user)
    
    def test_receipt_msisdn_normalization(self):
        send_sms = SendSMS.objects.create(user=self.user,
                                            msisdn='27761234567', 
                                            identifier='abcdefg',
                                            expiry=datetime.today() + timedelta(days=1),
                                            delivery=datetime.today())
        self.assertEquals(send_sms.status, 'v') # unknown
        
        raw_xml_post = """
        <?xml version="1.0"?>
        <!DOCTYPE receipts>
        <receipts>
          <receipt>
            <msgid>26567958</msgid>
            <reference>abcdefg</reference>
            <msisdn>+27761234567</msisdn>
            <status>D</status>
            <timestamp>20080831T15:59:24</timestamp>
            <billed>NO</billed>
          </receipt>
        </receipts>
        """
        
        from django.test.client import RequestFactory
        factory = RequestFactory(HTTP_AUTHORIZATION=basic_auth_string('user', 'password'))
        request = factory.post('/', raw_xml_post.strip(), content_type='application/xml; charset=utf-8;')
        request.user = User.objects.get(username='user')
        
        # ugly monkey patching to avoid us having to use a URL to test the opera
        # backend
        from txtalert.apps.gateway.backends.opera.views import sms_receipt_handler
        
        # mimick POSTed receipt from Opera
        add_perms_to_user('user','can_place_sms_receipt')
        
        # push the request
        response = sms_receipt_handler(request)
        
        # check the database response
        updated_send_sms = SendSMS.objects.get(pk=send_sms.pk)
        self.assertEquals(updated_send_sms.user, self.user)
        self.assertEquals(updated_send_sms.status, 'D') # delivered
        
    
    def test_bad_receipt_processing(self):
        """Test behaviour when we receive a receipt that doesn't match
        anything we know"""
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
            [send_sms] = gateway.send_sms(self.user, [receipt.msisdn], ['testing %s' % receipt.reference])
            # manually specifiy the identifier so we can compare it later with the
            # posted receipt
            send_sms.identifier = 'a-bad-id' # this is going to cause a failure
            send_sms.save()
        
        # mimick POSTed receipt from Opera
        add_perms_to_user('user','can_place_sms_receipt')
        
        from django.test.client import RequestFactory
        factory = RequestFactory(HTTP_AUTHORIZATION=basic_auth_string('user', 'password'))
        request = factory.post('/', raw_xml_post.strip(), content_type='application/xml; charset=utf-8;')
        request.user = User.objects.get(username='user')
        
        from txtalert.apps.gateway.backends.opera.views import sms_receipt_handler
        response = sms_receipt_handler(request)
        
        # it should return a JSON response
        self.assertEquals(response['Content-Type'], 'application/json; charset=utf-8')
        
        # test the json response
        from django.utils import simplejson
        data = simplejson.loads(response.content)
        self.assertTrue(data.keys(), ['fail','success'])
        # all should've failed
        self.assertEquals(len(data['fail']), 2)
        # we should get the dict back representing the receipt
        self.assertEquals([r._asdict() for r in receipts], data['fail'])
        
        # check database state
        for receipt in receipts:
            self.assertRaises(
                SendSMS.DoesNotExist,   # exception expected
                SendSMS.objects.get,    # callback
                user=self.user,       # args
                msisdn=receipt.msisdn,  
                identifier=receipt.reference
            )
    


class SmsGatewayTestCase(TestCase):
    """Testing the opera gateway interactions"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='user', \
                                                email='user@domain.com', \
                                                password='password')
    
    def test_send_sms(self):
        [send_sms,] = gateway.send_sms(self.user, ['27123456789'],['testing'])
        self.failUnless(send_sms.user == self.user)
        self.failUnless(SendSMS.objects.filter(user=self.user, msisdn='27123456789'))
    
    def test_json_sms_statistics_auth(self):
        response = self.client.get(reverse('api-sms',kwargs={'emitter_format':'json'}), 
                                    HTTP_AUTHORIZATION=basic_auth_string('invalid','user'))
        self.assertEquals(response.status_code, 401) # Http Basic Auth
        
        add_perms_to_user('user', 'can_view_sms_statistics')
        
        response = self.client.get(reverse('api-sms',kwargs={'emitter_format':'json'}), {
            "since": datetime.now().strftime(SendSMS.TIMESTAMP_FORMAT)
            }, 
            HTTP_AUTHORIZATION=basic_auth_string('user','password'))
        
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/json; charset=utf-8')
    
    def test_json_sms_statistics_bad_request(self):
        add_perms_to_user('user', 'can_view_sms_statistics')
        response = self.client.get(
            reverse('api-sms', kwargs={'emitter_format':'json'}), 
            {}, # not providing the `since` parameter, should return a bad request
            HTTP_AUTHORIZATION=basic_auth_string('user','password')
        )
        
        self.assertEquals(response.status_code, 400) # Bad request
        self.assertEquals(response['Content-Type'], 'text/plain')
    
    def test_json_sms_statistics_with_msisdn_and_identifier(self):
        add_perms_to_user('user', 'can_view_sms_statistics')
        
        # this should raise an error becasue the SendSMS with these attributes
        # doesn't exist yet
        def do_request():
            return self.client.get(
                reverse('api-sms', kwargs={
                    'emitter_format': 'json',
                    'identifier': 'a' * 8,
                    'msisdn': '27123456789'
                }),
                {},
                HTTP_AUTHORIZATION=basic_auth_string('user', 'password')
            )
        response = do_request()
        self.assertEquals(response.status_code, 500) 
        
        # now create it and repeat
        sms = SendSMS.objects.create(
            user=self.user,
            identifier='a' * 8, 
            msisdn='27123456789',
            delivery=datetime.now(),
            expiry=datetime.now(),
            smstext='',
            priority='Standard',
            receipt='Y',
        )
        response = do_request()
        self.assertEquals(response['Content-Type'], 'application/json; charset=utf-8')
        data = simplejson.loads(response.content)
        self.assertEquals(data['status'], sms.status)
        self.assertEquals(data['msisdn'], sms.msisdn)
        self.assertEquals(data['identifier'], 'a' * 8)
    
    def test_send_sms_json_response(self):
        add_perms_to_user('user', 'can_send_sms')
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
        self.assertEquals(receipt['msisdn'], '27123456789')
    
    def test_send_multiple_sms_response(self):
        add_perms_to_user('user', 'can_send_sms')
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
            self.assertTrue(receipt['msisdn'] in ['27123456789', '27123456781'])
    
    def test_send_too_large_sms(self):
        add_perms_to_user('user', 'can_send_sms')
        
        response = self.client.post(reverse('api-sms',kwargs={'emitter_format':'json'}), simplejson.dumps({
                'msisdns': ['27123456789'],
                'smstext': 'a' * 161 # 1 char too large
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=basic_auth_string('user','password'))
        self.assertEquals(response.status_code, 400) # HttpResponseBadRequest
    

class PcmAutomationTestCase(TestCase):
    
    fixtures = ['contacts.json']
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user',
                                                email='user@domain.com',
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
    
    def test_voicemail_message_receiving(self):
        add_perms_to_user('user', 'can_place_pcm')
        
        def submit_message(msg):
            parameters = {
                'sender_msisdn': '121',
                'recipient_msisdn': '27123456789',
                'sms_id': 'doesntmatteratm',
                'message': msg
            }
            response = self.client.post(reverse('api-pcm', kwargs={'emitter_format': 'json'}),
                parameters,
                HTTP_AUTHORIZATION=basic_auth_string('user', 'password')
            )
            self.assertEquals(response.status_code, 201) # Created
            return PleaseCallMe.objects.latest('created_at')
        
        sms = submit_message('You have 1 new message. The last message from 0712345671 was left at 11/04/2011 16:00. Please dial 121')
        self.assertEquals(
            sms.message,
            "Missed call from 0712345671, left at %s." % datetime(2011,4,11,16)
        )
        self.assertEquals(
            sms.sender_msisdn,
            '0712345671'
        )
        
        sms = submit_message('Missed call: 0712345672, 16:00 11/04/2011;')
        self.assertEquals(
            sms.message,
            "Missed call from 0712345672, left at %s." % datetime(2011,4,11,16)
        )
        self.assertEquals(
            sms.sender_msisdn,
            '0712345672'
        )
        
        # this isn't going to match, testing fail case
        fail_voicemail_sms = submit_message('Missed kall: 0712345678, 11/04/2011 16:00')
        self.assertEquals(
            fail_voicemail_sms.message,
            'Missed kall: 0712345678, 11/04/2011 16:00',
        )
        
        self.assertEquals(
            fail_voicemail_sms.sender_msisdn,
            '121'
        )
        
    def test_pcm_receiving_bad_request(self):
        add_perms_to_user('user', 'can_place_pcm')
        
        parameters = {
            # no parameters, should raise an error
        }
        
        response = self.client.post(
            reverse('api-pcm', kwargs={'emitter_format':'json'}),
            parameters,
            HTTP_AUTHORIZATION=basic_auth_string('user','password')
        )
        
        self.assertEquals(response.status_code, 400) # Bad Request
    
    def test_pcm_statistics(self):
        response = self.client.get(reverse('api-pcm', kwargs={'emitter_format':'json'}), 
                                HTTP_AUTHORIZATION=basic_auth_string('invalid', 'user'))
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
        response = self.client.get(reverse('api-pcm',kwargs={'emitter_format':'json'}), {
            "since": yesterday.strftime(SendSMS.TIMESTAMP_FORMAT)
            },
            HTTP_AUTHORIZATION=basic_auth_string('user','password')
        )
        
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/json; charset=utf-8')
        from django.utils import simplejson
        data = simplejson.loads(response.content)
        self.assertTrue(len(data) == 1)
        first_item = data[0]
        
        from txtalert.apps.api.handlers import PCMHandler
        
        # test the fields exposed by the PCMHandler
        for key in ('sms_id', 'sender_msisdn', 'recipient_msisdn'):
            self.assertEquals(parameters[key], first_item[key])
    
    def test_pcm_statistics_bad_request(self):
        add_perms_to_user('user', 'can_place_pcm')
        add_perms_to_user('user', 'can_view_pcm_statistics')
        response = self.client.get(
            reverse('api-pcm', kwargs={'emitter_format':'json'}), 
            {}, # missing `since` parameter should raise error
            HTTP_AUTHORIZATION=basic_auth_string('user','password')
        )
        
        self.assertEquals(response.status_code, 400)
    

        