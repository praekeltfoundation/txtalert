from django.test import TestCase
from therapyedge.models import *
from datetime import datetime

class ModelTestCase(TestCase):
    
    fixtures = ['patients', 'clinics', 'visits']
    
    def test_language_unicode(self):
        self.assertEquals(
            unicode(Language(name='english')),
            u'english'
        )
    
    def test_clinic_unicode(self):
        self.assertEquals(
            unicode(Clinic(name='clinic')),
            u'clinic'
        )
    
    def test_visit_unicode(self):
        self.assertEquals(
            unicode(Visit(visit_type='arv')),
            u'ARV'
        )
    
    def test_please_call_me_unicode(self):
        timestamp = datetime.now()
        msisdn = MSISDN.objects.create(msisdn='27123456789')
        self.assertEquals(
            unicode(PleaseCallMe(
                msisdn=msisdn,
                timestamp=timestamp
            )),
            u'%s - %s' % (msisdn, timestamp)
        )
    
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
        patient = Patient.objects.all()[0]
        self.assertEquals(patient.get_last_clinic(), None)
        self.assertEquals(patient.clinics(), [])
        
        visit = patient.visit_set.create(
            clinic=Clinic.objects.all()[0],
            date=datetime.now(),
            status='s'
        )
        
        self.assertTrue(visit.clinic in patient.clinics())
        self.assertEquals(visit.clinic, patient.get_last_clinic())