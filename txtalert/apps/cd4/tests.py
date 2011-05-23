from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from os.path import join
from txtalert.apps.cd4.utils import read_cd4_document
from txtalert.apps.cd4.models import CD4Document, CD4Record, CD4_MESSAGE_TEMPLATE
from txtalert.apps.gateway.models import SendSMS
from txtalert.apps import gateway
gateway.load_backend('txtalert.apps.gateway.backends.dummy')

class CD4TestCase(TestCase):
    
    fixtures = ['patients']
    
    def setUp(self):
        self.sample_file = join(settings.MEDIA_ROOT, settings.UPLOAD_ROOT, 
                                    'sample.xls')
        self.document = read_cd4_document(self.sample_file)
        self.user = User.objects.get(username='kumbu')
    
    def tearDown(self):
        pass
    
    def test_parsing_of_sample_excel(self):
        """
        We should be able to read the sample MS Excel document
        """
        # there should be 4 rows
        self.assertEquals(len(self.document), 4)
        for row in self.document:
            # each with 5 columns
            self.assertEquals(len(row), 5)
    
    def test_storing_of_sample_excel(self):
        document = CD4Document.objects.create(original=self.sample_file,
                                                user=self.user)
        self.assertEquals(document.record_set.count(), 4)
        for record in document.record_set.all():
            self.assertEquals(record.sms, None)
    
    def test_sending_of_loaded_records(self):
        document = CD4Document.objects.create(original=self.sample_file,
                                                user=self.user)
        document.send_messages()
        for record in document.record_set.all():
            self.assertTrue(isinstance(record.sms, SendSMS))
            self.assertEquals(record.sms.smstext, CD4_MESSAGE_TEMPLATE % record.cd4count)