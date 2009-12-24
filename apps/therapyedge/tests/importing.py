#  This file is part of TxtAlert.
#
#  TxtALert is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TxtAlert is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with TxtAlert.  If not, see <http://www.gnu.org/licenses/>.


from datetime import datetime, date
from django.test import TestCase
from therapyedge.models import *
from therapyedge.importer import Importer, InvalidValueException
from therapyedge.tests.utils import create_instance
from therapyedge.tests.utils import (PatientUpdate, ComingVisit, MissedVisit,
                                        DoneVisit, DeletedVisit)

def reload_record(record):
    return record.__class__.objects.get(pk=record.pk)

class PatientImportTestCase(TestCase):
    
    fixtures = ['clinics.json', 'patients.json',]
    
    def setUp(self):
        self.importer = Importer()
    
    def testInvalidAgeImport(self):
        # import an invalid patient record
        self.assertRaises(InvalidValueException,    # exception 
            self.importer.update_local_patient,     # callable
            create_instance(PatientUpdate, {        # args
                'te_id': '01-1235', 
                'age': '3135', 
                'sex': 'Female', 
                'celphone': '082123'
            })
        )
    
    def testInvalidSexImport(self):
        # import an invalid patient record
        self.assertRaises(InvalidValueException,    # exception
            self.importer.update_local_patient,     # callable 
            create_instance(PatientUpdate, {        # args
                'te_id': '01-1235', 
                'age': '31', 
                'sex': 'Feale', 
                'celphone': '082123'
            })
        )
    
    def testBasicImport(self):
        """basic patient record import"""
        patient = self.importer.update_local_patient(create_instance(PatientUpdate, {
            'te_id': '03-12345', 
            'age': '25', 
            'sex': 'Male', 
            'celphone': '0821231234'
        }))
        # reload to make sure we have the database values
        patient = reload_record(patient)
        
        self.assertEquals(patient.te_id, '03-12345')
        self.assertEquals(patient.age, 25)
        self.assertEquals(patient.sex, 'm')
        self.assertEquals(patient.msisdns.latest('id').msisdn, '27821231234')
        self.assertEquals(
            patient.history.latest().get_history_type_display(), 
            'Created'
        )
        
    
    def testAlterDetails(self):
        """duplicate 'te_id' import with altered details"""
        patient = self.importer.update_local_patient(create_instance(PatientUpdate, {
            'te_id': '02-12345', 
            'age': '35', 
            'sex': 'Female', 
            'celphone':'0821234321'
        }))
        patient = reload_record(patient)
        self.assertEquals(
            patient.history.latest().get_history_type_display(), 
            'Changed'
        )
        self.assertEquals(patient.age, 35)
        self.assertEquals(patient.sex, 'f')
        self.assertEquals(patient.msisdns.latest('id').msisdn, '27821234321')
        self.assertEquals(patient.history.count(), 2) # this is an update, should have 2 items in history
    
    def testDuplicateMsisdnImport(self):
        """duplicate 'msisdn' import"""
        # new patient, not in fixtures
        patientA = self.importer.update_local_patient(create_instance(PatientUpdate, {
            'te_id': '03-12345', 
            'age': '30', 
            'sex': 'Male', 
            'celphone': '0821111111'
        }))
        
        # existing patient, in fixtures
        patientB = self.importer.update_local_patient(create_instance(PatientUpdate, {
            'te_id': '01-12345', 
            'age': '30', 
            'sex': 'Male', 
            'celphone': '0821111111'
        }))
        
        patientA = reload_record(patientA)
        patientB = reload_record(patientB)
        
        self.assertEquals(
            patientA.history.latest().get_history_type_display(), 
            'Created'
        )
        
        self.assertEquals(
            patientB.history.latest().get_history_type_display(), 
            'Changed'
        )
        
        # both phone numbers should point to the same MSISDN record 
        # in the database
        self.assertEqual(
            patientA.msisdns.latest('id').id, 
            patientB.msisdns.latest('id').id
        )
    
    def testCountryCodeMsisdn(self):
        """country code included in 'msisdn'"""
        patient = self.importer.update_local_patient(create_instance(PatientUpdate, {
            'te_id': '03-12345', 
            'age': '55', 
            'sex': 'Male', 
            'celphone': '+27823211234'
        }))
        patient = reload_record(patient)
        self.assertEquals(patient.history.latest().get_history_type_display(), 
                            'Created')
        self.assertEquals(patient.msisdns.latest('id').msisdn, '27823211234')
    
    def testMultipleMsisdn(self):
        """multiple 'msisdn' import (ons country code 'msisdn' without plus)"""
        patient = self.importer.update_local_patient(create_instance(PatientUpdate, {
            'te_id': '03-12345', 
            'age': '18', 
            'sex': 'Female', 
            'celphone': '0821231111/27821232222'
        }))
        patient = reload_record(patient)
        self.assertEquals(patient.history.latest().get_history_type_display(), 
                            'Created')
        
        msisdns = patient.msisdns.all()
        self.assertEqual(len(msisdns), 2)
        self.assertEqual(msisdns[0].msisdn, '27821231111')
        self.assertEqual(msisdns[1].msisdn, '27821232222')
    

class VisitImportTestCase(TestCase):
    fixtures = ['patients.json', 'clinics.json', 'visits.json',]
    
    def setUp(self):
        self.clinic = Clinic.objects.get(te_id='01')
        self.importer = Importer()
    
    def testInvalidImport(self):
        """attempt import of an invalid record"""
        self.assertRaises(Patient.DoesNotExist,         # exception
            self.importer.update_local_coming_visit,    # callback
            self.clinic,                                # arg1
            create_instance(                            # arg2
                ComingVisit, {
                'key_id': '123456789', 
                'te_id': '01-1245', 
                'scheduled_visit_date':'2080-26 00:00:00'
            })
        )
    
    def testNewVisit(self):
        """import a new visit"""
        visit = self.importer.update_local_coming_visit(
            self.clinic,
            create_instance(ComingVisit, {
                'key_id': '02-123456789', 
                'te_id': '01-12345', 
                'scheduled_visit_date': '2100-06-01 00:00:00'
            })
        )
        visit = reload_record(visit)
        self.assertEqual(visit.history.latest().get_history_type_display(), 
                            'Created')
        self.assertEquals(visit.te_visit_id, '02-123456789')
        self.assertEquals(visit.patient.te_id, '01-12345')
        self.assertEquals(visit.date, date(2100, 6, 1))

    def testIndicateReschedule(self):
        """reschedule a visit"""
        visit = self.importer.update_local_missed_visit(
            self.clinic,
            create_instance(MissedVisit, {
                'key_id': '01-123456789', 
                'te_id': '01-12345', 
                'missed_date': '2100-05-01 00:00:00' # future date should be seen as a reschedule
            })
        )
        visit = reload_record(visit)
        self.assertEqual(visit.history.latest().get_history_type_display(), 
                            'Changed')
        self.assertEquals(visit.status, 'r')
        self.assertEquals(visit.date, date(2100, 5, 1))

    def testIndicateMissed(self):
        # indicate a missed visit
        event = importMissedVisit(self.event, self.clinic, {'key_id':'01-123456789', 'te_id':'01-12345', 'missed_date':'2100-06-01 00:00:00'})
        self.assertEqual(event.type, 'update')
        visit = models.Visit.objects.get(te_visit_id='01-123456789')
        self.assertEquals(visit.status, 'm')
        self.assertEquals(visit.date, datetime(2100, 6, 1).date())

    def testIndicateAttended(self):
        # indicate a attended visit
        event = importDoneVisit(self.event, self.clinic, {'key_id':'01-123456789', 'te_id':'01-12345', 'done_date':'2100-07-01 00:00:00'})
        self.assertEqual(event.type, 'update')
        visit = models.Visit.objects.get(te_visit_id='01-123456789')
        self.assertEquals(visit.status, 'a')
        self.assertEquals(visit.date, datetime(2100, 7, 1).date())

    def testIndicateNewAttended(self):
        # indicate a new attended visit
        event = importDoneVisit(self.event, self.clinic, {'key_id':'02-123456789', 'te_id':'01-12345', 'done_date':'2100-07-01 00:00:00'})
        self.assertEqual(event.type, 'new')
        visit = models.Visit.objects.get(te_visit_id='02-123456789')
        self.assertEquals(visit.status, 'a')
        self.assertEquals(visit.date, datetime(2100, 7, 1).date())

    def testIndicateNewMissed(self):
        # indicate a new attended visit
        yesterday = datetime.now() - timedelta(days=1)
        event = importMissedVisit(self.event, self.clinic, {
            'key_id':'02-123456789', 
            'te_id':'01-12345', 
            'missed_date': yesterday.strftime('%Y-%m-%d 00:00:00')
        })
        self.assertEqual(event.type, 'new')
        visit = models.Visit.objects.get(te_visit_id='02-123456789')
        self.assertEquals(visit.status, 'm')
        self.assertEquals(visit.date, yesterday.date())

    def testDelete(self):
        # delete an visit
        event = importDeletedVisit(self.event, self.clinic, {'key_id':'01-123456789', 'te_id':'01-12345'})
        self.assertEqual(event.type, 'update')
        self.assertEqual(models.Visit.objects.count(), 0)


class PatientRiskProfileTestCase(TestCase):
    fixtures = ['clinics.json', 'patients.json',]
    
    def setUp(self):
        self.patient = models.Patient.objects.all()[0]
        self.clinic = models.Clinic.objects.get(te_id='01')
        self.event = ImportEvent()
        
    def reload_patient(self):
        return models.Patient.objects.get(pk=self.patient.id)

    def test_risk_profile_calculation(self):
        today = datetime.now() - timedelta(days=1)
        event = importMissedVisit(self.event, self.clinic, {
            'key_id':'02-123456789', 
            'te_id':self.patient.te_id, 
            'missed_date': today.strftime('%Y-%m-%d 00:00:00')
        })
        self.assertEquals(self.reload_patient().risk_profile, 1.0)
    
    def test_risk_profile_incremental_calculation(self):
        yesterday = datetime.now() - timedelta(days=1)
        two_days_ago = yesterday - timedelta(days=1)
        importDoneVisit(self.event, self.clinic, {
            'key_id':'02-123456701', 
            'te_id':self.patient.te_id, 
            'done_date':'2100-07-01 00:00:00'
        })
        importDoneVisit(self.event, self.clinic, {
            'key_id':'02-123456702', 
            'te_id':self.patient.te_id, 
            'done_date':'2100-07-02 00:00:00'
        })
        self.assertEquals(self.reload_patient().risk_profile, 0.0)
        importMissedVisit(self.event, self.clinic, {
            'key_id':'02-123456703', 
            'te_id':self.patient.te_id, 
            'missed_date': yesterday.strftime('%Y-%m-%d 00:00:00')
        })
        self.assertAlmostEquals(self.reload_patient().risk_profile, 0.33, places=2)
        importMissedVisit(self.event, self.clinic, {
            'key_id':'02-123456704', 
            'te_id':self.patient.te_id, 
            'missed_date': two_days_ago.strftime('%Y-%m-%d 00:00:00')
        })
        self.assertAlmostEquals(self.reload_patient().risk_profile, 0.50, places=2)
