from django.test import TestCase
from txtalert.core.models import *
from django.contrib.auth.models import Group
from datetime import datetime

class PermissionsTestCase(TestCase):
    
    fixtures = ['patients','clinics','visits']
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    # def test_msisdn_access(self):
    #     assert False
    # 
    # def test_patient_access(self):
    #     assert False
    # 
    # def test_clinic_access(self):
    #     assert False
    # 
    # def test_visit_acess(self):
    #     assert False
    


class ModelTestCase(TestCase):
    
    fixtures = ['patients', 'clinics', 'visits']
    
    def test_patient_soft_delete(self):
        patient = Patient.objects.all()[0]
        patient.delete()
        # regular get fails because it is flagged as deleted
        self.assertRaises(
            Patient.DoesNotExist,
            Patient.objects.get,
            pk=patient.pk
        )
        # the all_objects manager however, should expose it
        self.assertEquals(patient, Patient.all_objects.get(pk=patient.pk))
    
    def test_patient_clinics(self):
        patient = Patient.objects.filter(last_clinic=None)[0]
        self.assertEquals(patient.get_last_clinic(), None)
        self.assertEquals(patient.clinics(), set([]))
        
        visit = patient.visit_set.create(
            clinic=Clinic.objects.all()[0],
            date=datetime.now(),
            status='s'
        )
        
        self.assertTrue(visit.clinic in patient.clinics())
        self.assertEquals(visit.clinic, patient.get_last_clinic())


from django.test import TestCase
from txtalert.apps.gateway.models import PleaseCallMe as GatewayPleaseCallMe
from txtalert.core.models import PleaseCallMe, Patient, Clinic, MSISDN
from datetime import datetime, timedelta

class PleaseCallMeTestCase(TestCase):
    
    fixtures = ['patients', 'clinics', 'visits']
    
    def setUp(self):
        # use dummy gateway
        from txtalert.apps import gateway
        gateway.load_backend('txtalert.apps.gateway.backends.dummy')
        
        self.user = User.objects.get(username="kumbu")
        
        self.patient = Patient.objects.all()[0]
        self.patient.save() # save to specify the active_msisdn
        
        # create a number of visits for this patient at a clinic
        for i in range(0,10):
            self.patient.visit_set.create(
                clinic=Clinic.objects.get(name='Test Clinic'),
                date=datetime.now() + timedelta(days=i),
                status='s'
            )
        
        self.assertTrue(self.patient.visit_set.all())
        self.assertTrue(self.patient.active_msisdn) # make sure that actually worked
        self.assertTrue(self.patient.get_last_clinic())
        self.assertTrue(self.patient.last_clinic)
        
    
    def tearDown(self):
        pass
    
    def test_please_call_me_from_gateway(self):
        # we should have non registered
        self.assertEquals(PleaseCallMe.objects.count(), 0)
        
        gpcm = GatewayPleaseCallMe.objects.create(
            sms_id='sms_id',
            sender_msisdn=self.patient.active_msisdn.msisdn,
            recipient_msisdn='27123456789',
            user=self.user,
            message='Please Call Me',
        )
        
        # we should have one registered through the signals
        self.assertEquals(PleaseCallMe.objects.count(), 1)
        pcm = PleaseCallMe.objects.latest('timestamp')
        self.assertEquals(pcm.msisdn, self.patient.active_msisdn)
        self.assertEquals(pcm.clinic, self.patient.last_clinic)
        self.assertEquals(pcm.message, gpcm.message)
    
    def test_please_call_me_from_therapyedge(self):
        pcm = PleaseCallMe.objects.create(
            msisdn = self.patient.active_msisdn,
            timestamp = datetime.now(),
            user = self.user,
        )
        # the signals should track the clinic for this pcm if it hasn't
        # been specified automatically yet
        self.assertEquals(pcm.clinic, Clinic.objects.get(name='Test Clinic'))
    
    def test_pcm_for_nonexistent_msisdn(self):
        # verify this nr doesn't exist in the db
        self.assertRaises(
            MSISDN.DoesNotExist,
            MSISDN.objects.get,
            msisdn='27123456789'
        )
        # this shouldn't raise an error, it should fail silently leaving
        # message in the log file
        gpcm = GatewayPleaseCallMe.objects.create(
            sms_id='sms_id',
            sender_msisdn='27123456789', # this shouldn't exist in the db
            user=self.user,
        )
    
    def test_multiple_patients_for_one_msisdn(self):
        msisdn = MSISDN.objects.create(msisdn='27123456789')
        for i in range(0,2):
            Patient.objects.create(
                active_msisdn = msisdn,
                owner=self.user,
                te_id='06-%s2345' % i,
                age=23
            )
        # we have two patients for the same msisdn
        self.assertEquals(
            Patient.objects.filter(active_msisdn=msisdn).count(),
            2
        )
        # this shouldn't raise an error, it should fail silently leaving
        # message in the log file
        gpcm = GatewayPleaseCallMe.objects.create(
            sms_id='sms_id',
            sender_msisdn=msisdn.msisdn,
            user=self.user,
        )
    
    def test_sloppy_get_or_create_possible_msisdn(self):
        msisdn = MSISDN.objects.create(msisdn='27123456121')
        from txtalert.core.signals import sloppy_get_or_create_possible_msisdn
        self.assertEquals(
            sloppy_get_or_create_possible_msisdn('121').msisdn,
            '121'
        )
        self.assertEquals(
            sloppy_get_or_create_possible_msisdn('0123456121').msisdn,
            '27123456121'
        )
        self.assertEquals(
            sloppy_get_or_create_possible_msisdn('27123456121').msisdn,
            '27123456121'
        )
        self.assertEquals(
            sloppy_get_or_create_possible_msisdn('+27123456121').msisdn,
            '27123456121'
        )
    
    def test_voicemail_notification_handling(self):
        from txtalert.apps.api.handlers import handle_voicemail_message
        sample_messages = [
            "Missed call: 07123456789, 16:17 11/04/2011;",
            "You have 1 new message. The last message from 07123456788 was left at 11/04/2010 15:17. Please dial 121.",
        ]
        msisdn, date = handle_voicemail_message(sample_messages[0])
        self.assertEquals(msisdn, '07123456789')
        self.assertEquals(date, datetime(2011,4,11,16,17))
        
        msisdn, date = handle_voicemail_message(sample_messages[1])
        self.assertEquals(msisdn, '07123456788')
        self.assertEquals(date, datetime(2010,4,11,15,17))
