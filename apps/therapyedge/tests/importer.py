from django.test import TestCase
from therapyedge.importer import Importer, SEX_MAP
from therapyedge.xmlrpc import client
from therapyedge.models import Patient, MSISDN, Visit, Clinic
from therapyedge.tests.utils import (PatientUpdate, ComingVisit, MissedVisit,
                                        DoneVisit, DeletedVisit)
from datetime import datetime, timedelta
import random
import logging
import iso8601

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
            '%s' % idx,                         # age, as string
            random.choice(SEX_MAP.keys()),      # sex
            '2712345678%s' % idx,               # celphone
            random.choice(('true','false')),    # dr_status
            '02-7012%s' % idx                   # te_id
        ) for idx in range(0, 10)]
        updated_patients = map(PatientUpdate._make, data)
        local_patients = list(self.importer.update_local_patients(updated_patients))
        self.assertEquals(len(local_patients), 10)
        
        for updated_patient in updated_patients:
            local_patient = Patient.objects.get(te_id=updated_patient.te_id)
            
            # check for msisdn
            msisdn = MSISDN.objects.get(msisdn=updated_patient.celphone)
            self.assertTrue(msisdn in local_patient.msisdns.all())
            
            # check for age
            self.assertEquals(local_patient.age, int(updated_patient.age))
            
            # check for sex
            self.assertEquals(local_patient.sex, SEX_MAP[updated_patient.sex])
            
            # check for te_id
            self.assertEquals(local_patient.te_id, updated_patient.te_id)
    
    def test_update_local_coming_visits(self):
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
            
            # the visit should have the same done date
            self.assertEquals(
                iso8601.parse_date(done_visit.done_date).date(),
                local_visit.date
            )
            
            # the visit should have the status of a, 'attended'
            self.assertEquals(
                local_visit.status,
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
    


class PatchedClient(client.Client):
    
    def __init__(self, **kwargs):
        self.patches = kwargs
    
    def rpc_call(self, request, *args, **kwargs):
        """Mocking the response we get from TherapyEdge for a patients_update
        call"""
        if request in self.patches:
            logging.debug('Mocked rpc_call called with: %s, %s, %s' % (request, args, kwargs))
            return self.patches[request]
        else:
            print 'request not patched', request
            return super(PatchedClient, self).rpc_call(request, *args, **kwargs)

class ImporterXmlRpcClientTestCase(TestCase):
    
    fixtures = ['patients', 'clinics']
    
    def setUp(self):
        self.importer = Importer()
        
        # patching the client to automatically return our specified result
        # sets without doing an XML-RPC call
        patched_client = PatchedClient(
            patients_update=[{
                    'dr_site_name': '',
                    'dr_site_id': '',
                    'age': '2%s' % i,
                    'sex': random.choice(['Male', 'Female']),
                    'celphone': '2712345678%s' % i,
                    'dr_status': '',
                    'te_id': patient.te_id,
                } for i, patient in enumerate(Patient.objects.all())],
            comingvisits=[{
                    'dr_site_name': '',
                    'dr_site_id': '',
                    'dr_status': '',
                    'scheduled_visit_date': str(datetime.now() + timedelta(days=2)),
                    'key_id': '02-1234%s' % i,
                    'te_id': patient.te_id,
                } for i, patient in enumerate(Patient.objects.all())],
            missedvisits=[{
                    'dr_site_name': '',
                    'dr_site_id': '',
                    'missed_date': str(datetime.now() - timedelta(days=2)), 
                    'dr_status': '', 
                    'key_id': '03-1234%s' % i, 
                    'te_id': patient.te_id
                } for i, patient in enumerate(Patient.objects.all())],
            donevisits=[{
                    'done_date': str(datetime.now() - timedelta(days=2)), 
                    'dr_site_id': '', 
                    'dr_status': '', 
                    'dr_site_name': '', 
                    'scheduled_date': str(datetime.now() - timedelta(days=2)), 
                    'key_id': '04-1234%s' % i, 
                    'te_id': patient.te_id
                } for i, patient in enumerate(Patient.objects.all())],
            deletedvisits=[{
                    'key_id': '02-1234%s' % i,
                    'dr_status': '',
                    'dr_site_id': '',
                    'te_id': patient.te_id,
                    'dr_site_name': ''
                } for i, patient in enumerate(Patient.objects.all())]
        )
        # monkey patching
        self.importer.client.rpc_call = patched_client.rpc_call
        
        self.clinic = Clinic.objects.all()[0] # make sure we have a clinic
        self.assertTrue(Patient.objects.count()) # make sure our fixtures aren't empty
    
    def tearDown(self):
        pass
    
    def test_import_updated_patients(self):
        """The xmlrpc client is largely some boilterplate code and some little
        helpers that transform the returned Dict into class instances. We're
        testing that functionality here. Since all the stuff uses the same boiler
        plate code we're only testing it for one method call.
        """
        updated_patients = self.importer.import_updated_patients(
            clinic=self.clinic, 
            since=(datetime.now() - timedelta(days=1)),
            until=datetime.now()
        )
        updated_patients = list(updated_patients)
        self.assertTrue(len(updated_patients), Patient.objects.count())
        self.assertTrue(isinstance(updated_patients[0], Patient))
    
    def test_import_coming_visits(self):
        coming_visits = self.importer.import_coming_visits(
            clinic=self.clinic,
            since=(datetime.now() - timedelta(days=1)),
            until=datetime.now()
        )
        coming_visits = list(coming_visits)
        self.assertEquals(len(coming_visits), Patient.objects.count())
        self.assertTrue(isinstance(coming_visits[0], Visit))
    
    def test_missed_visits(self):
        missed_visits = self.importer.import_missed_visits(
            clinic=self.clinic,
            since=(datetime.now() - timedelta(days=1)),
            until=datetime.now()
        )
        missed_visits = list(missed_visits)
        self.assertEquals(len(missed_visits), Patient.objects.count())
        self.assertTrue(isinstance(missed_visits[0], Visit))
    
    def test_done_visits(self):
        done_visits = self.importer.import_done_visits(
            clinic=self.clinic,
            since=(datetime.now() - timedelta(days=1)),
            until=datetime.now()
        )
        done_visits = list(done_visits)
        self.assertEquals(len(done_visits), Patient.objects.count())
        self.assertTrue(isinstance(done_visits[0], Visit))
    
    def test_deleted_visits(self):
        # first have some coming visits
        coming_visits = list(self.importer.import_coming_visits(
            clinic=self.clinic,
            since=(datetime.now() - timedelta(days=1)),
            until=datetime.now()
        ))
        # then mark them as deleted, they're matched because they
        # have the same key_id
        deleted_visits = list(self.importer.import_deleted_visits(
            since=(datetime.now() - timedelta(days=1)),
            until=datetime.now()
        ))
        self.assertEquals(len(deleted_visits), Patient.objects.count())
        self.assertTrue(isinstance(deleted_visits[0], Visit))