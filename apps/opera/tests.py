from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from opera.views import element_to_namedtuple
import xml.etree.ElementTree as ET
from opera.gateway import Gateway
from opera.models import SendSMS
from datetime import datetime

class OperaTestingGateway(object):
    """Dummy gateway we used to monkey patch the real RPC gateway so we can write
    our test code against something we control"""
    
    def use_identifier(self, identifier):
        """specify what identifier to return"""
        self.identifier = identifier
    
    def SendSMS(self, args):
        return {'Identifier': self.identifier}
    

class OperaTestCase(TestCase):
    """Testing the opera gateway interactions"""
    def setUp(self):
        self.client = Client()
        self.gateway = Gateway('http://testserver/', 'service_id', 'password', \
                                'channel', verbose=True)
        # specify the proxy's EAPIGateway, which is what Opera uses internally
        setattr(self.gateway.proxy, 'EAPIGateway', OperaTestingGateway())
        
        # add a helper function to set the identifier
        def use_identifier(identifier):
            self.gateway.proxy.EAPIGateway.use_identifier(identifier)
        setattr(self.gateway, 'use_identifier', use_identifier)
    
    def test_send_sms(self):
        """we've hijacked the EAPIGateway and tell it what to return as the 
        identifier. The SendSMS object should store that identifier after 
        communicating with the RPC gateway"""
        self.gateway.use_identifier('12345678')
        [send_sms,] = self.gateway.send_sms(['27764493806'],['testing'])
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
            self.gateway.use_identifier(receipt.reference)
            self.gateway.send_sms([receipt.msisdn], ['testing %s' % receipt.reference])
        
        response = self.client.post(reverse('sms-receipt'), raw_xml_post.strip(), \
                                    content_type='text/xml')
        
        for receipt in receipts:
            send_sms = SendSMS.objects.get(number=receipt.msisdn, identifier=receipt.reference)
            self.assertEquals(send_sms.delivery_timestamp.strftime(SendSMS.TIMESTAMP_FORMAT), receipt.timestamp)
            self.assertEquals(send_sms.status, 'D')
        