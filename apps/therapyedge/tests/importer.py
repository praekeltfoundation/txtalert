from django.test import TestCase
from collections import namedtuple
from therapyedge.importer import Importer, SEX_MAP
from therapyedge.models import Patient, MSISDN, Visit, Clinic
from datetime import datetime, timedelta
import random
import iso8601

# These classes are generated on the fly by the client, the client has
# a call to class name map and reads the attribute names from the dict
# returned by TherapyEdge's XML-RPC service
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

MissedVisit = namedtuple('MissedVisit', [
    'dr_site_name',
    'dr_site_id',
    'missed_date', 
    'dr_status', 
    'key_id', 
    'te_id'
])

DoneVisit = namedtuple('DoneVisit', [
    'done_date', 
    'dr_site_id', 
    'dr_status', 
    'dr_site_name', 
    'scheduled_date', 
    'key_id', 
    'te_id'
])

DeletedVisit = namedtuple('DeletedVisit', [
    'key_id',
    'dr_status',
    'dr_site_id',
    'te_id',
    'dr_site_name'
])

class ImporterTestCase(TestCase):
    """Testing the TherapyEdge import loop"""
    
    fixtures = ['patients', 'clinics']
    
    def setUp(self):
        self.importer = Importer()
        # make sure we're actually testing some data
        self.assertTrue(Patient.objects.count() > 0)
        self.clinic = Clinic.objects.all()[0]
    
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
            patient.te_id,                  # te_id
        ) for idx, patient in enumerate(Patient.objects.all())]
        coming_visits = map(ComingVisit._make, data)
        
        local_visits = set(self.importer.update_local_coming_visits(
            self.clinic, 
            coming_visits
        ))
        self.assertEquals(len(local_visits), Patient.objects.count())
        
        for coming_visit in coming_visits:
            # don't need to test this as Django does this for us
            local_visit = Visit.objects.get(te_visit_id=coming_visit.key_id)
            self.assertEquals(
                iso8601.parse_date(coming_visit.scheduled_visit_date).date(),
                local_visit.date
            )
    
    def test_update_local_missed_visits(self):
        data = [(
            '',                                 # dr_site_name
            '',                                 # dr_site_id
            '2009-11-1%s 00:00:00' % idx,       # missed_date
            '',                                 # dr_status
            '02-00089421%s' % idx,              # key_id
            patient.te_id,                      # te_id
        ) for idx, patient in enumerate(Patient.objects.all())]
        missed_visits = map(MissedVisit._make, data)
        local_visits = set(self.importer.update_local_missed_visits(
            self.clinic, 
            missed_visits
        ))
        self.assertEquals(len(local_visits), Patient.objects.count())
        for missed_visit in missed_visits:
            local_visit = Visit.objects.get(te_visit_id=missed_visit.key_id)
            self.assertEquals(
                iso8601.parse_date(missed_visit.missed_date).date(),
                local_visit.date
            )
    
    def test_update_local_done_visits(self):
        data = [(
          '2009-11-1%s 00:00:00' % idx, # done_date 
          '',                           # dr_site_id 
          '',                           # dr_status
          '',                           # dr_site_name
          '2009-10-1%s 00:00:00' % idx, # scheduled_date, mocked to be a month earlier
          '02-00089421%s' % idx,        # key_id
          patient.te_id,                # te_id
        ) for idx, patient in enumerate(Patient.objects.all())]
        done_visits = map(DoneVisit._make, data)
        local_visits = set(self.importer.update_local_done_visits(
            self.clinic,
            done_visits
        ))
        self.assertEquals(len(local_visits), Patient.objects.count())
        for done_visit in done_visits:
            local_visit = Visit.objects.get(te_visit_id=done_visit.key_id)
            
            # the main event should have the same scheduled date
            self.assertEquals(
                iso8601.parse_date(done_visit.scheduled_date).date(),
                local_visit.date
            )
            
            # the visit event itself should have the same done date
            visit_event = local_visit.events.latest('date')
            self.assertEquals(
                iso8601.parse_date(done_visit.done_date).date(),
                visit_event.date
            )
            
            # the visit event should have the status of a, 'attended'
            self.assertEquals(
                visit_event.status,
                'a'
            )
    
    def test_update_local_deleted_visits(self):
        
        # first create the visit events to be deleted
        data = [(
            '',                             # dr_site_name 
            '',                             # dr_site_id
            'false',                        # dr_status 
            '2009-11-1%s 00:00:00' % idx,   # scheduled_visit_date
            '02-00089421%s' % idx,          # key_id
            patient.te_id,                  # te_id
        ) for idx, patient in enumerate(Patient.objects.all())]
        coming_visits = map(ComingVisit._make, data)
        local_visits = set(self.importer.update_local_coming_visits(
            self.clinic, 
            coming_visits
        ))
        self.assertEquals(len(coming_visits), len(local_visits))
        
        data = [(
            '02-00089421%s' % idx,  # key_id
            'false',                # dr_status
            '',                     # dr_site_id
            patient.te_id,          # te_id
            '',                     # dr_site_name
        ) for idx, patient in enumerate(Patient.objects.all())]
        deleted_visits = map(DeletedVisit._make, data)
        # use list comprihensions because set() dedupes the list and for some
        # reason it considers deleted the deleted django objects as dupes
        # and returns a list of one
        local_visits = [v for v in self.importer.update_local_deleted_visits(
            deleted_visits
        )]
        self.assertEquals(len(local_visits), Patient.objects.count())
        for deleted_visit in deleted_visits:
            self.assertEquals(
                Visit.objects.filter(te_visit_id=deleted_visit.key_id).count(), 
                0
            )
