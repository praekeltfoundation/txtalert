from django.test import TestCase
from django.db import IntegrityError
from txtalert.apps.googledoc.models import SpreadSheet, GoogleAccount
from txtalert.apps.googledoc.importer import Importer
from txtalert.apps.googledoc.reader.spreadsheetReader import SimpleCRUD
from txtalert.core.models import Patient, MSISDN, Visit, Clinic
from datetime import datetime, timedelta, date
import logging
import random

class Importer_tester(TestCase):
    """Testing the google spreadsheet import loop"""
    
    fixtures = ['patient', 'visit']
    
    def setUp(self):
        #dummy google login details
        self.email = 'txtalert@byteorbit.com'
        self.password = 'testtest'
        self.importer = Importer(self.email, self.password)
        # make sure we're actually testing some data
        self.assertTrue(Patient.objects.count() > 0)
        self.assertTrue(Visit.objects.count() > 0)
        self.month_worksheet = { 
                                     1: {'appointmentdate1': date(2011, 8, 1), 'fileno': 1111111, 'appointmentstatus1': 'Missed', 'phonenumber': 123456789}, 
                                     2: {'appointmentdate1': date(2011, 8, 10), 'fileno': 9999999, 'appointmentstatus1': 'Scheduled', 'phonenumber': 987654321}, 
                        }

    def tearDown(self):
        pass
        
    def test_invalid_file_no_(self):
        """Test if the file no is invalid."""
        self.patient_row = {'appointmentdate1': date(2011, 8, 10), 'fileno': 'gggggg', 'appointmentstatus1': 'Missed', 'phonenumber': 987654321}
        self.row_no = 2
        self.file_no = self.importer.updatePatient(self.patient_row, self.row_no)
        self.assertIs(self.file_no, self.patient_row['fileno'])
    
    def test_invalid_patient_id(self):
        """Patient not on the database."""
        self.patient_row = {'appointmentdate1': date(2011, 8, 10), 'fileno': 555555, 'appointmentstatus1': 'Missed', 'phonenumber': 987654321}
        self.row_no = 2
        self.exists = self.importer.updatePatient(self.patient_row, self.row_no)
        self.assertEqual(self.exists, False)
    
    def test_successful_patient_update(self):
        """Test that a patient was successfully updated."""
        self.patient_row = {'appointmentdate1': date(2011, 8, 9), 'fileno': 9999999, 'appointmentstatus1': 'Attended', 'phonenumber': 987654321}
        self.row_no = 2
        self.patient_updated = self.importer.updatePatient(self.patient_row, self.row_no)
        self.assertEqual(self.patient_updated, True)
     
    def test_msisdn_format(self):
        """Test the format of the phone number."""
        #invalid phone number formats
        self.phones = [1234567, 123456789012, '+1234567', '012456789', '-12345678901', '###12345']
        #random selection of invalid phone numbers 
        self.phone_test = random.choice(self.phones)
        self.curr_patient = Patient.objects.get(te_id='02-9999999')
        #phone number and format correct flag
        self.phone, self.format = self.importer.updateMSISDN(self.phone_test, self.curr_patient)
        self.assertIs(self.format, False)
        self.assertEquals(self.phone_test, self.phone)
        
    def test_updated_msisdn(self):
        """Test that the phone number was updated."""
        self.msisdn = random.choice(range(111111111, 999999999, 123456))
        self.msisdn = '27' + str(self.msisdn)
        self.curr_patient = Patient.objects.get(te_id='02-9999999')
        self.assertTrue(self.curr_patient)
        self.phone, self.created = self.importer.updateMSISDN(self.msisdn, self.curr_patient)
        self.assertIs(self.created, True)
        self.assertEquals(self.msisdn, self.phone)
        
    def test_msisdn_not_updated(self):
        """Test if incorrect phone number are not updated """
        self.msisdn = random.choice(range(1111111, 9999999, 12345))
        self.curr_patient = Patient.objects.get(te_id='02-9999999')
        self.assertTrue(self.curr_patient)
        self.phone, self.created = self.importer.updateMSISDN(self.msisdn, self.curr_patient)
        self.phone = int(self.phone)
        self.assertIs(self.created, False)
        self.assertEqual(self.msisdn, self.phone)
       
       
    def test_invalid_visit_id(self):
        """Visit not on the database."""
        (self.app_status, self.app_date, self.visit_id) = ('Scheduled', date(2011, 8, 10), 'jjjjjjj')
        self.visit_exists = self.importer.updateAppointmentStatus(self.app_status, self.app_date, self.visit_id)
        self.assertIs(self.visit_exists, False)
        
    def test_update_not_needed(self):
        """Appointment status already updated."""
        (self.app_status, self.app_date, self.visit_id) = ('Scheduled', date(2011, 8, 10), '02-9999999')
        self.updated = self.importer.updateAppointmentStatus(self.app_status, self.app_date, self.visit_id)
        self.assertEquals(self.updated, True)
        
    def test_status_is_updated(self):
        """Checks that the status was updated"""
        (self.app_status, self.app_date, self.visit_id) = ('Missed', date(2011, 8, 10), '02-9999999')
        self.status_updated = self.importer.updateAppointmentStatus(self.app_status, self.app_date, self.visit_id)
        self.assertEquals(self.status_updated, 'm')
    
    def test_status_not_updated(self):
        """Test that the update failed."""
        (self.app_status, self.app_date, self.visit_id) = ('Missed', date(2011, 8, 1), '02-9999999')
        self.status_updated = self.importer.updateAppointmentStatus(self.app_status, self.app_date, self.visit_id)
        self.assertEquals(self.status_updated, 'm')     