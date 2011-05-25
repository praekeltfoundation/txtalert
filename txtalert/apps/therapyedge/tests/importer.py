from django.test import TestCase
from django.contrib.auth.models import User
from txtalert.apps.therapyedge.importer import Importer, SEX_MAP
from txtalert.apps.therapyedge.xmlrpc import client
from txtalert.core.models import Patient, MSISDN, Visit, Clinic
from txtalert.apps.therapyedge.tests.utils import (PatientUpdate, ComingVisit, MissedVisit,
                                        DoneVisit, DeletedVisit, create_instance)
from datetime import datetime, timedelta, date
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
        self.user = User.objects.get(username="kumbu")
    
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
        local_patients = list(self.importer.update_local_patients(self.user, updated_patients))
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
            self.user,
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
            self.user,
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
    
    def test_missed_visits(self):
        # helper methods
        def make_visit(named_tuple_klass, dictionary):
            return named_tuple_klass._make(named_tuple_klass._fields) \
                                                        ._replace(**dictionary)
        # mock patient
        patient = Patient.objects.all()[0]
        # create a visit that's already been scheduled earlier, mock a 
        # previous import
        visit = patient.visit_set.create(
            te_visit_id='02-002173383',
            date=date.today(), 
            status='s',
            clinic=self.clinic
        )
        # create a missed visit
        missed_visit = make_visit(MissedVisit, {
            'dr_site_name': '', 
            'dr_site_id': '', 
            'dr_status': 'false', 
            'missed_date': '%s 00:00:00' % date.today(), 
            'key_id': '02-002173383', 
            'te_id': patient.te_id
        })
        # import the data
        list(self.importer.update_local_missed_visits(self.user, self.clinic, [missed_visit]))
        # get the visit and check its status
        visit = patient.visit_set.get(te_visit_id='02-002173383')
        self.assertEquals(visit.status, 'm')
    
    def test_update_local_reschedules_from_missed(self):
        """missed visits in the future are reschedules"""
        future_date = date.today() + timedelta(days=7) # one week ahead
        # first plan the scheduleds
        data = [(
            '',                             # dr_site_name 
            '',                             # dr_site_id
            'false',                        # dr_status
            # scheduled_visit_date, force to start one day ahead of today 
            # to make sure they're always future dates
            '%s 00:00:00' % (date.today() + timedelta(days=(idx+1))),
            '02-00089421%s' % idx,          # key_id
            patient.te_id,                  # te_id
        ) for idx, patient in enumerate(Patient.objects.all())]
        coming_visits = map(ComingVisit._make, data)
        
        local_visits = set(self.importer.update_local_coming_visits(
            self.user,
            self.clinic, 
            coming_visits
        ))
        self.assertEquals(len(local_visits), Patient.objects.count())
        
        for coming_visit in coming_visits:
            # don't need to test this as Django does this for us
            local_visit = Visit.objects.get(te_visit_id=coming_visit.key_id)
            self.assertEquals('s', local_visit.status)
        
        
        # now plan the future misseds, should be reschedules
        data = [(
            '',                                 # dr_site_name
            '',                                 # dr_site_id
            '%s 00:00:00' % future_date,        # missed_date
            '',                                 # dr_status
            '02-00089421%s' % idx,              # key_id
            patient.te_id,                      # te_id
        ) for idx, patient in enumerate(Patient.objects.all())]
        rescheduled_visits = map(MissedVisit._make, data)
        local_visits = set(self.importer.update_local_missed_visits(
            self.user,
            self.clinic,
            rescheduled_visits
        ))
        self.assertEquals(len(local_visits), Patient.objects.count())
        for rescheduled_visit in rescheduled_visits:
            local_visit = Visit.objects.get(te_visit_id=rescheduled_visit.key_id)
            self.assertEquals(local_visit.status, 'r')
    
    def test_update_local_reschedules_from_coming(self):
        """future visits that get a new date in the future are reschedules"""
        data = [(
            '',                             # dr_site_name 
            '',                             # dr_site_id
            'false',                        # dr_status
            # scheduled_visit_date, force to start one day ahead of today 
            # to make sure they're always future dates
            '%s 00:00:00' % (date.today() + timedelta(days=(idx+1))),
            '02-00089421%s' % idx,          # key_id
            patient.te_id,                  # te_id
        ) for idx, patient in enumerate(Patient.objects.all())]
        coming_visits = map(ComingVisit._make, data)
        
        local_visits = set(self.importer.update_local_coming_visits(
            self.user,
            self.clinic, 
            coming_visits
        ))
        self.assertEquals(len(local_visits), Patient.objects.count())
        
        for coming_visit in coming_visits:
            # don't need to test this as Django does this for us
            local_visit = Visit.objects.get(te_visit_id=coming_visit.key_id)
            self.assertEquals('s', local_visit.status)
        
        # send in a batch of future coming visits to mimick reschedules
        future_date = date.today() + timedelta(days=7) # one week ahead
        data = [(
            '',                             # dr_site_name 
            '',                             # dr_site_id
            'false',                        # dr_status 
            '%s 00:00:00' % future_date,    # scheduled_visit_date
            '02-00089421%s' % idx,          # key_id
            patient.te_id,                  # te_id
        ) for idx, patient in enumerate(Patient.objects.all())]
        coming_visits = map(ComingVisit._make, data)
        set(self.importer.update_local_coming_visits(self.user, self.clinic, coming_visits))
        for coming_visit in coming_visits:
            local_visit = Visit.objects.get(te_visit_id=coming_visit.key_id)
            self.assertEquals('r', local_visit.status)
    
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
            self.user,
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
            self.user,
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
            self.user,
            deleted_visits
        )]
        self.assertEquals(len(local_visits), Patient.objects.count())
        for deleted_visit in deleted_visits:
            self.assertEquals(
                Visit.objects.filter(te_visit_id=deleted_visit.key_id).count(), 
                0
            )
    
    def test_for_history_duplication(self):
        """
        Test for history duplication happening after numerous imports over time
        
        The data for this test has been gleaned from the txtalert log being 
        used in production. For some reason imports that should be 'missed' 
        are set as 'rescheduled' and eventhough nothing changes in the 
        appointment, a historical visit is still saved.
        """
        
        # create the patient for which we'll get the visits
        patient = Patient.objects.create(te_id='02-82088', age=29, sex='m',
                                            owner=self.user)
        
        # importer
        importer = Importer()
        # [importer] 2010-03-18 08:00:37,705 DEBUG Processing coming Visit {'dr_site_name': '', 'dr_site_id': '', 'dr_status': 'false', 'scheduled_visit_date': '2010-03-24 00:00:00', 'key_id': '02-091967084', 'te_id': '02-82088'}
        coming_visit = create_instance(ComingVisit, {'dr_site_name': '', 'dr_site_id': '', 'dr_status': 'false', 'scheduled_visit_date': '2010-03-24 00:00:00', 'key_id': '02-091967084', 'te_id': '02-82088'})
        local_coming_visit = importer.update_local_coming_visit(self.user, self.clinic, coming_visit)
        # [importer] 2010-03-18 08:01:39,354 DEBUG Processing missed Visit: {'dr_site_name': '', 'dr_site_id': '', 'missed_date': '2010-03-24 00:00:00', 'dr_status': 'false', 'key_id': '02-091967084', 'te_id': '02-82088'}
        missed_visit = create_instance(MissedVisit, {'dr_site_name': '', 'dr_site_id': '', 'missed_date': '2010-03-24 00:00:00', 'dr_status': 'false', 'key_id': '02-091967084', 'te_id': '02-82088'})
        local_missed_visit = importer.update_local_missed_visit(self.user, self.clinic, missed_visit)
        # [importer] 2010-03-19 08:00:36,876 DEBUG Processing coming Visit {'dr_site_name': '', 'dr_site_id': '', 'dr_status': 'false', 'scheduled_visit_date': '2010-03-24 00:00:00', 'key_id': '02-091967084', 'te_id': '02-82088'}
        coming_visit = create_instance(ComingVisit, {'dr_site_name': '', 'dr_site_id': '', 'dr_status': 'false', 'scheduled_visit_date': '2010-03-24 00:00:00', 'key_id': '02-091967084', 'te_id': '02-82088'})
        local_coming_visit = importer.update_local_coming_visit(self.user, self.clinic, coming_visit)
        # [importer] 2010-03-19 08:01:36,747 DEBUG Processing missed Visit: {'dr_site_name': '', 'dr_site_id': '', 'missed_date': '2010-03-24 00:00:00', 'dr_status': 'false', 'key_id': '02-091967084', 'te_id': '02-82088'}
        missed_visit = create_instance(MissedVisit, {'dr_site_name': '', 'dr_site_id': '', 'missed_date': '2010-03-24 00:00:00', 'dr_status': 'false', 'key_id': '02-091967084', 'te_id': '02-82088'})
        local_missed_visit = importer.update_local_missed_visit(self.user, self.clinic, missed_visit)
        # [importer] 2010-03-20 08:00:29,600 DEBUG Processing coming Visit {'dr_site_name': '', 'dr_site_id': '', 'dr_status': 'false', 'scheduled_visit_date': '2010-03-24 00:00:00', 'key_id': '02-091967084', 'te_id': '02-82088'}
        coming_visit = create_instance(ComingVisit, {'dr_site_name': '', 'dr_site_id': '', 'dr_status': 'false', 'scheduled_visit_date': '2010-03-24 00:00:00', 'key_id': '02-091967084', 'te_id': '02-82088'})
        local_coming_visit = importer.update_local_coming_visit(self.user, self.clinic, coming_visit)
        # [importer] 2010-03-20 08:01:30,926 DEBUG Processing missed Visit: {'dr_site_name': '', 'dr_site_id': '', 'missed_date': '2010-03-24 00:00:00', 'dr_status': 'false', 'key_id': '02-091967084', 'te_id': '02-82088'}
        missed_visit = create_instance(MissedVisit, {'dr_site_name': '', 'dr_site_id': '', 'missed_date': '2010-03-24 00:00:00', 'dr_status': 'false', 'key_id': '02-091967084', 'te_id': '02-82088'})
        local_missed_visit = importer.update_local_missed_visit(self.user, self.clinic, missed_visit)
        # [importer] 2010-03-21 08:00:28,052 DEBUG Processing coming Visit {'dr_site_name': '', 'dr_site_id': '', 'dr_status': 'false', 'scheduled_visit_date': '2010-03-24 00:00:00', 'key_id': '02-091967084', 'te_id': '02-82088'}
        coming_visit = create_instance(ComingVisit, {'dr_site_name': '', 'dr_site_id': '', 'dr_status': 'false', 'scheduled_visit_date': '2010-03-24 00:00:00', 'key_id': '02-091967084', 'te_id': '02-82088'})
        local_coming_visit = importer.update_local_coming_visit(self.user, self.clinic, coming_visit)
        # [importer] 2010-03-21 08:01:33,909 DEBUG Processing missed Visit: {'dr_site_name': '', 'dr_site_id': '', 'missed_date': '2010-03-24 00:00:00', 'dr_status': 'false', 'key_id': '02-091967084', 'te_id': '02-82088'}
        missed_visit = create_instance(MissedVisit, {'dr_site_name': '', 'dr_site_id': '', 'missed_date': '2010-03-24 00:00:00', 'dr_status': 'false', 'key_id': '02-091967084', 'te_id': '02-82088'})
        local_missed_visit = importer.update_local_missed_visit(self.user, self.clinic, missed_visit)
        # [importer] 2010-03-22 08:00:27,711 DEBUG Processing coming Visit {'dr_site_name': '', 'dr_site_id': '', 'dr_status': 'false', 'scheduled_visit_date': '2010-03-24 00:00:00', 'key_id': '02-091967084', 'te_id': '02-82088'}
        coming_visit = create_instance(ComingVisit, {'dr_site_name': '', 'dr_site_id': '', 'dr_status': 'false', 'scheduled_visit_date': '2010-03-24 00:00:00', 'key_id': '02-091967084', 'te_id': '02-82088'})
        local_coming_visit = importer.update_local_coming_visit(self.user, self.clinic, coming_visit)
        # [importer] 2010-03-22 08:01:33,549 DEBUG Processing missed Visit: {'dr_site_name': '', 'dr_site_id': '', 'missed_date': '2010-03-24 00:00:00', 'dr_status': 'false', 'key_id': '02-091967084', 'te_id': '02-82088'}
        missed_visit = create_instance(MissedVisit, {'dr_site_name': '', 'dr_site_id': '', 'missed_date': '2010-03-24 00:00:00', 'dr_status': 'false', 'key_id': '02-091967084', 'te_id': '02-82088'})
        local_missed_visit = importer.update_local_missed_visit(self.user, self.clinic, missed_visit)
        # [importer] 2010-03-23 08:00:26,453 DEBUG Processing coming Visit {'dr_site_name': '', 'dr_site_id': '', 'dr_status': 'false', 'scheduled_visit_date': '2010-03-24 00:00:00', 'key_id': '02-091967084', 'te_id': '02-82088'}
        coming_visit = create_instance(ComingVisit, {'dr_site_name': '', 'dr_site_id': '', 'dr_status': 'false', 'scheduled_visit_date': '2010-03-24 00:00:00', 'key_id': '02-091967084', 'te_id': '02-82088'})
        local_coming_visit = importer.update_local_coming_visit(self.user, self.clinic, coming_visit)
        # [importer] 2010-03-23 08:01:36,731 DEBUG Processing missed Visit: {'dr_site_name': '', 'dr_site_id': '', 'missed_date': '2010-03-24 00:00:00', 'dr_status': 'false', 'key_id': '02-091967084', 'te_id': '02-82088'}
        missed_visit = create_instance(MissedVisit, {'dr_site_name': '', 'dr_site_id': '', 'missed_date': '2010-03-24 00:00:00', 'dr_status': 'false', 'key_id': '02-091967084', 'te_id': '02-82088'})
        local_missed_visit = importer.update_local_missed_visit(self.user, self.clinic, missed_visit)
        # [importer] 2010-03-25 09:00:41,774 DEBUG Processing coming Visit {'dr_site_name': '', 'dr_site_id': '', 'dr_status': 'false', 'scheduled_visit_date': '2010-03-24 00:00:00', 'key_id': '02-091967084', 'te_id': '02-82088'}
        coming_visit = create_instance(ComingVisit, {'dr_site_name': '', 'dr_site_id': '', 'dr_status': 'false', 'scheduled_visit_date': '2010-03-24 00:00:00', 'key_id': '02-091967084', 'te_id': '02-82088'})
        local_coming_visit = importer.update_local_coming_visit(self.user, self.clinic, coming_visit)
        # [importer] 2010-03-25 09:00:41,850 DEBUG Updating existing Visit: 37361 / ({'date': datetime.date(2010, 3, 24), 'updated_at': datetime.datetime(2010, 3, 23, 8, 1, 36)} vs {'status': u'r', 'comment': u'', 'visit_type': u'', 'deleted': 0, 'created_at': datetime.datetime(2010, 3, 18, 8, 0, 37), 'updated_at': datetime.datetime(2010, 3, 23, 8, 1, 36), 'te_visit_id': u'02-091967084', 'date': datetime.date(2010, 3, 24), 'id': 37361L})
        # [importer] 2010-03-25 09:01:40,902 DEBUG Processing missed Visit: {'dr_site_name': '', 'dr_site_id': '', 'missed_date': '2010-03-24 00:00:00', 'dr_status': 'false', 'key_id': '02-091967084', 'te_id': '02-82088'}
        missed_visit = create_instance(MissedVisit, {'dr_site_name': '', 'dr_site_id': '', 'missed_date': '2010-03-24 00:00:00', 'dr_status': 'false', 'key_id': '02-091967084', 'te_id': '02-82088'})
        local_missed_visit = importer.update_local_missed_visit(self.user, self.clinic, missed_visit)
        
        visit = patient.visit_set.latest()
        
        self.assertEquals(visit.status, 'm')
        self.assertEquals(visit.history.count(), 1)
        
        done_visit = create_instance(DoneVisit, {'dr_site_name': '', 'dr_site_id': '', 'done_date': '2010-03-24 00:00:00', 'scheduled_date': '2010-03-24 00:00:00', 'dr_status': 'false', 'key_id': '02-091967084', 'te_id': '02-82088'})
        local_done_visit = importer.update_local_done_visit(self.user, self.clinic, done_visit)
        
        visit = patient.visit_set.latest()
        self.assertEquals(visit.status, 'a')
        self.assertEquals(visit.history.count(), 2)
    


class PatchedClient(client.Client): 
    def __init__(self, **kwargs):
        self.patches = kwargs
    
    def rpc_call(self, request, *args, **kwargs):
        """Mocking the response we get from TherapyEdge for a patients_update
        call"""
        logging.debug('Mocked rpc_call called with: %s, %s, %s' % (request, args, kwargs))
        return self.patches[request]

class ImporterXmlRpcClientTestCase(TestCase):
    
    fixtures = ['patients', 'clinics']
    
    def setUp(self):
        self.importer = Importer()
        self.user = User.objects.get(username="kumbu")
        
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
            user=self.user,
            clinic=self.clinic, 
            since=(datetime.now() - timedelta(days=1)),
            until=datetime.now()
        )
        updated_patients = list(updated_patients)
        self.assertTrue(len(updated_patients), Patient.objects.count())
        self.assertTrue(isinstance(updated_patients[0], Patient))
    
    def test_import_coming_visits(self):
        coming_visits = self.importer.import_coming_visits(
            user=self.user,
            clinic=self.clinic,
            since=(datetime.now() - timedelta(days=1)),
            until=datetime.now()
        )
        coming_visits = list(coming_visits)
        self.assertEquals(len(coming_visits), Patient.objects.count())
        self.assertTrue(isinstance(coming_visits[0], Visit))
    
    def test_missed_visits(self):
        missed_visits = self.importer.import_missed_visits(
            user=self.user,
            clinic=self.clinic,
            since=(datetime.now() - timedelta(days=1)),
            until=datetime.now()
        )
        missed_visits = list(missed_visits)
        self.assertEquals(len(missed_visits), Patient.objects.count())
        self.assertTrue(isinstance(missed_visits[0], Visit))
    
    def test_done_visits(self):
        done_visits = self.importer.import_done_visits(
            user=self.user,
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
            user=self.user,
            clinic=self.clinic,
            since=(datetime.now() - timedelta(days=1)),
            until=datetime.now()
        ))
        # then mark them as deleted, they're matched because they
        # have the same key_id
        deleted_visits = list(self.importer.import_deleted_visits(
            user=self.user,
            clinic=self.clinic,
            since=(datetime.now() - timedelta(days=1)),
            until=datetime.now()
        ))
        self.assertEquals(len(deleted_visits), Patient.objects.count())
        self.assertTrue(isinstance(deleted_visits[0], Visit))
    

