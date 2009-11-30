from django.test import TestCase
from collections import namedtuple
from therapyedge.importer import Importer, SEX_MAP
from therapyedge.models import Patient, MSISDN
from datetime import datetime, timedelta
import random

PatientUpdate = namedtuple('PatientUpdate', [
    'dr_site_name', 
    'dr_site_id', 
    'age', 
    'sex', 
    'celphone',  # TherapyEdge's typo
    'dr_status', 
    'te_id'
])

ComingVisit = namedtuple('ComingVisit', [
    'dr_site_name',
    'dr_site_id',
    'dr_status',
    'scheduled_visit_date',
    'key_id',
    'te_id'
])

class ImporterTestCase(TestCase):
    """Testing the TherapyEdge import loop"""
    
    def setUp(self):
        self.importer = Importer()
    
    def tearDown(self):
        pass
    
    def test_update_local_patients(self):
        """Test the mapping of the incoming Patient objects to local copies"""
        # mock received data from TherapyEdge XML-RPC
        data = [(
            '',                                 # dr_site_id
            '',                                 # dr_site_name
            idx,                                # age
            random.choice(SEX_MAP.keys()),      # sex
            '27012345678%s' % idx,              # celphone
            random.choice(('true','false')),    # dr_status
            '02-7012%s' % idx                   # te_id
        ) for idx in range(0,10)]
        updated_patients = map(PatientUpdate._make, data)
        local_patients = set(self.importer.update_local_patients(updated_patients))
        self.assertEquals(len(local_patients), 10)
        
        for updated_patient in updated_patients:
            local_patient = Patient.objects.get(te_id=updated_patient.te_id)
            
            # check for msisdn
            msisdn = MSISDN.objects.get(msisdn=updated_patient.celphone)
            self.assertTrue(msisdn in local_patient.msisdns.all())
            
            # check for age
            self.assertEquals(local_patient.age, updated_patient.age)
            
            # check for sex
            self.assertEquals(local_patient.sex, SEX_MAP[updated_patient.sex])
            
            # check for te_id
            self.assertEquals(local_patient.te_id, updated_patient.te_id)
    
    def test_update_local_coming_visits(self):
        # from therapyedge.xmlrpc import client
        # client.introspect(clinic_id='02',
        #     since=datetime.now() - timedelta(days=3),
        #     until=datetime.now() + timedelta(days=10)
        # )
        data = [(
            '',                             # dr_site_name 
            '',                             # dr_site_id
            'false',                        # dr_status 
            '2009-11-1%s 00:00:00' % idx,   # scheduled_visit_date
            '02-00089421%s' % idx,          # key_id
            '02-1075%s' % idx,              # te_id
        ) for idx in range(0,10)]
        coming_visits = map(ComingVisit._make, data)
        local_visits = set(self.importer.update_local_coming_visits(coming_visits))
        self.assertEquals(len(local_visits), 10)