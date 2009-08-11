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


import datetime
from django.test import TestCase
from therapyedge.providers.te import *
from therapyedge import models


class PatientImportTestCase(TestCase):
    fixtures = ['clinics.json', 'patients.json',]

    def setUp(self):
        self.clinic = models.Clinic.objects.get(te_id='01')
        self.event = ImportEvent()

    def testInvalidImport(self):
        # import an invalid patient record
        event = importPatient(self.event, self.clinic, {'te_id':'01-1235', 'age':'3135', 'sex':'Feale', 'celphone':'082123'})
        self.assertEquals(event.type, 'error')
        self.assertEquals(len(event.messages), 4)

    def testBasicImport(self):
        # basic patient record import
        event = importPatient(self.event, self.clinic, {'te_id':'03-12345', 'age':'25', 'sex':'Male', 'celphone':'0821231234'})
        self.assertEquals(event.type, 'new')
        patient = models.Patient.objects.get(te_id='03-12345')
        self.assertEquals(patient.age, 25)
        self.assertEquals(patient.sex, 'm')
        self.assertEquals(patient.msisdns.all()[0].msisdn, '27821231234')

    def testAlterDetails(self):
        # duplicate 'te_id' import with altered details
        event = importPatient(self.event, self.clinic, {'te_id':'02-12345', 'age':'35', 'sex':'Female', 'celphone':'0821234321'})
        self.assertEquals(event.type, 'update')
        patient = models.Patient.objects.get(te_id='02-12345')
        self.assertEquals(patient.age, 35)
        self.assertEquals(patient.sex, 'f')
        self.assertEquals(patient.msisdns.all()[0].msisdn, '27821234321')

    def testDuplicateMsisdnImport(self):
        # duplicate 'msisdn' import
        event = importPatient(self.event, self.clinic, {'te_id':'03-12345', 'age':'30', 'sex':'Male', 'celphone':'0821111111'})
        self.assertEquals(event.type, 'new')
        patientA = models.Patient.objects.get(te_id='01-12345')
        patientB = models.Patient.objects.get(te_id='03-12345')
        self.assertEqual(patientA.msisdns.all()[0].id, patientB.msisdns.all()[0].id)

    def testCountryCodeMsisdn(self):
        # country code included in 'msisdn'
        event = importPatient(self.event, self.clinic, {'te_id':'03-12345', 'age':'55', 'sex':'Male', 'celphone':'+27823211234'})
        self.assertEquals(event.type, 'new')
        patient = models.Patient.objects.get(te_id='03-12345')
        self.assertEquals(patient.msisdns.all()[0].msisdn, '27823211234')

    def testMultipleMsisdn(self):
        # multiple 'msisdn' import (ons country code 'msisdn' without plus)
        event = importPatient(self.event, self.clinic, {'te_id':'03-12345', 'age':'18', 'sex':'Female', 'celphone':'0821231111/27821232222'})
        self.assertEquals(event.type, 'new')
        patient = models.Patient.objects.get(te_id='03-12345')
        msisdns = patient.msisdns.all()
        self.assertEqual(len(msisdns), 2)
        self.assertEqual(msisdns[0].msisdn, '27821231111')
        self.assertEqual(msisdns[1].msisdn, '27821232222')


class VisitImportTestCase(TestCase):
    fixtures = ['patients.json', 'clinics.json', 'visits.json',]

    def setUp(self):
        self.clinic = models.Clinic.objects.get(te_id='01')
        self.event = ImportEvent()

    def testInvalidImport(self):
        # attempt import of an invalid record
        event = importComingVisit(self.event, self.clinic, {'key_id':'123456789', 'te_id':'01-1245', 'scheduled_visit_date':'2080-26 00:00:00'})
        self.assertEqual(event.type, 'error')
        self.assertEquals(len(event.messages), 3)

    def testNewVisit(self):
        # import a new visit
        event = importComingVisit(self.event, self.clinic, {'key_id':'02-123456789', 'te_id':'01-12345', 'scheduled_visit_date':'2100-06-01 00:00:00'})
        self.assertEqual(event.type, 'new')
        visit = models.Visit.objects.get(te_id='02-123456789')
        self.assertEquals(visit.te_id, '02-123456789')
        self.assertEquals(visit.patient.te_id, '01-12345')
        self.assertEquals(visit.date, datetime(2100, 6, 1).date())

    def testIndicateReschedule(self):
        # reschedule an visit
        event = importMissedVisit(self.event, self.clinic, {'key_id':'01-123456789', 'te_id':'01-12345', 'missed_date':'2100-05-01 00:00:00'})
        self.assertEqual(event.type, 'update')
        visit = models.Visit.objects.get(te_id='01-123456789')
        event = visit.events.all()[0]
        self.assertEquals(event.status, 'r')
        self.assertEquals(event.date, datetime(2100, 5, 1).date())

    def testIndicateMissed(self):
        # indicate a missed visit
        event = importMissedVisit(self.event, self.clinic, {'key_id':'01-123456789', 'te_id':'01-12345', 'missed_date':'2100-06-01 00:00:00'})
        self.assertEqual(event.type, 'update')
        visit = models.Visit.objects.get(te_id='01-123456789')
        event = visit.events.all()[0]
        self.assertEquals(event.status, 'm')
        self.assertEquals(event.date, datetime(2100, 6, 1).date())

    def testIndicateAttended(self):
        # indicate a attended visit
        event = importDoneVisit(self.event, self.clinic, {'key_id':'01-123456789', 'te_id':'01-12345', 'done_date':'2100-07-01 00:00:00'})
        self.assertEqual(event.type, 'update')
        visit = models.Visit.objects.get(te_id='01-123456789')
        event = visit.events.all()[0]
        self.assertEquals(event.status, 'a')
        self.assertEquals(event.date, datetime(2100, 7, 1).date())

    def testIndicateNewAttended(self):
        # indicate a new attended visit
        event = importDoneVisit(self.event, self.clinic, {'key_id':'02-123456789', 'te_id':'01-12345', 'done_date':'2100-07-01 00:00:00'})
        self.assertEqual(event.type, 'new')
        visit = models.Visit.objects.get(te_id='02-123456789')
        event = visit.events.all()[0]
        self.assertEquals(event.status, 'a')
        self.assertEquals(event.date, datetime(2100, 7, 1).date())

    def testIndicateNewMissed(self):
        # indicate a new attended visit
        event = importMissedVisit(self.event, self.clinic, {'key_id':'02-123456789', 'te_id':'01-12345', 'missed_date':'2100-07-01 00:00:00'})
        self.assertEqual(event.type, 'new')
        visit = models.Visit.objects.get(te_id='02-123456789')
        event = visit.events.all()[0]
        self.assertEquals(event.status, 'm')
        self.assertEquals(event.date, datetime(2100, 7, 1).date())

    def testDelete(self):
        # delete an visit
        event = importDeletedVisit(self.event, self.clinic, {'key_id':'01-123456789', 'te_id':'01-12345'})
        self.assertEqual(event.type, 'update')
        self.assertEqual(models.Visit.objects.count(), 0)
