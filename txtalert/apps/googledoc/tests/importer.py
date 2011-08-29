from django.test import TestCase
from django.db import IntegrityError
from txtalert.apps.googledoc.models import SpreadSheet, GoogleAccount
from txtalert.apps.googledoc.importer import Importer
from txtalert.apps.googledoc.reader.spreadsheetReader import SimpleCRUD
from txtalert.core.models import Patient, MSISDN, Visit, Clinic
from datetime import datetime, timedelta, date
from gdata.service import BadAuthentication
import logging
import random

class Importer_tester(TestCase):
    """Testing the google spreadsheet import loop"""
    
    fixtures = ['patient', 'visit', 'clinic']
    
    def setUp(self):
        #dummy google login details
        self.email = 'txtalert@byteorbit.com'
        self.password = 'testtest'
        self.spreadsheet = 'Praekelt'
        self.start = date.today() - timedelta(days=14) 
        self.until = date.today()
        self.importer = Importer(self.email, self.password)
        # make sure we're actually testing some data
        self.assertTrue(Patient.objects.count() > 0)
        self.assertTrue(Visit.objects.count() > 0)
        self.assertTrue(Clinic.objects.count() > 0)
        self.enrolled_patients = { 
                                     1: {'appointmentdate1': date(2011, 8, 1), 'fileno': 1111111, 'appointmentstatus1': 'Missed', 'phonenumber': 999999999}, 
                                     2: {'appointmentdate1': date(2011, 8, 10), 'fileno': 9999999, 'appointmentstatus1': 'Attended', 'phonenumber': 111111111}, 
                        }

    def tearDown(self):
        pass
             
    def test_update_patients(self):
        """Test if a worksheet of patients is updated successfully."""
        (self.enrolled_counter, self.correct_updates) = self.importer.update_patients(self.enrolled_patients, self.spreadsheet, self.start, self.until)
        self.assertEqual(self.enrolled_counter, 2)
        self.assertEqual(self.correct_updates, 2)        
        
    def test_invalid_file_no_(self):
        """Test if the file no is invalid."""
        #invalid phone number formats
        self.files = ['+1234', '#ab789', 'abc8901@@', 'ab#12345']
        #random selection of invalid file numbers 
        self.file_test = random.choice(self.files)
        self.patient_row = {'appointmentdate1': date(2011, 8, 10), 'fileno': self.file_test, 'appointmentstatus1': 'Missed', 'phonenumber': 987654321}
        self.row_no = 2
        self.file_no = self.importer.update_patient(self.patient_row, self.row_no)
        self.assertIs(self.file_no, self.patient_row['fileno'])
    
    def test_invalid_patient_id(self):
        """Patient not on the database."""
        self.patient_row = {'appointmentdate1': date(2011, 8, 10), 'fileno': 555555, 'appointmentstatus1': 'Missed', 'phonenumber': 987654321}
        self.row_no = 2
        self.exists = self.importer.update_patient(self.patient_row, self.row_no)
        self.assertEqual(self.exists, False)
    
    def test_successful_patient_update(self):
        """Test that a patient was successfully updated."""
        self.patient_row = {'appointmentdate1': date(2011, 8, 9), 'fileno': 9999999, 'appointmentstatus1': 'Attended', 'phonenumber': 987654321}
        self.row_no = 2
        self.patient_updated = self.importer.update_patient(self.patient_row, self.row_no)
        self.assertEqual(self.patient_updated, True)
     
    def test_msisdn_format(self):
        """Test the format of the phone number."""
        #invalid phone number formats
        self.phones = [1234567, 123456789012, '+1234567', '012456789', '-12345678901', '###12345']
        #random selection of invalid phone numbers 
        self.phone_test = random.choice(self.phones)
        self.curr_patient = Patient.objects.get(te_id='9999999')
        #phone number and format correct flag
        self.phone, self.format = self.importer.updateMSISDN(self.phone_test, self.curr_patient)
        self.assertIs(self.format, False)
        self.assertEquals(self.phone_test, self.phone)
        
    def test_updated_msisdn(self):
        """Test that the phone number was updated."""
        self.msisdn = random.choice(range(111111111, 999999999, 123456))
        self.msisdn = '27' + str(self.msisdn)
        self.curr_patient = Patient.objects.get(te_id='9999999')
        self.assertTrue(self.curr_patient)
        self.phone, self.created = self.importer.updateMSISDN(self.msisdn, self.curr_patient)
        self.assertIs(self.created, True)
        self.assertEquals(self.msisdn, self.phone)
        
    def test_msisdn_not_updated(self):
        """Test if incorrect phone number are not updated """
        self.msisdn = random.choice(range(1111111, 9999999, 12345))
        self.curr_patient = Patient.objects.get(te_id='9999999')
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
        
             
class SpreadSheetReaderTestCase(TestCase):
    
    
    def setUp(self):
        self.email = 'txtalert@byteorbit.com'
        self.password = 'testtest'
        self.spreadsheet = 'Praekelt'
        self.reader = SimpleCRUD(self.email, self.password)
        self.assertTrue(self.reader)
        self.start = date.today() - timedelta(days=14) 
        self.until = date.today()
        self.test_dict = {         
                       1: {
                            'appointmentdate1': date(2011, 8, 1),
                            'fileno': 9999999,
                            'appointmentstatus1': 'Scheduled', 
                            'phonenumber': 123456789
                          },
                       2: {
                           'appointmentdate1': date(2011, 8, 5), 
                           'fileno': 8888888, 
                           'appointmentstatus1': 'Scheduled', 
                           'phonenumber': 987654321  
                           }, 
                       3: {
                           'appointmentdate1': date(2011, 8, 11), 
                           'fileno': 7777777,
                           'appointmentstatus1': 'Scheduled',
                           'phonenumber': 741852963
                           },
                       4: {
                           'appointmentdate1': date(2011, 9, 2),
                           'fileno': 6666666,
                           'appointmentstatus1': 'Scheduled',
                           'phonenumber': 369258147
                           }
        }
        
    def tearDown(self):
        pass
         
    def test_get_spreadsheet(self):
        """Test for getting a spreadsheet that exists."""
        self.found = self.reader.get_spreadsheet(self.spreadsheet) 
        self.assertTrue(self.found) 
      
    def test_get_spreadsheet_fail(self):
        """Test for getting a spreadsheet that does not exists."""
        self.fail_spreadsheet = '##########'
        self.not_found = self.reader.get_spreadsheet(self.fail_spreadsheet) 
        self.assertEqual(self.not_found, False)
        
    def test_appointment_rows(self):
        """
        Test for getting the appointments in a worksheet
        that fall between the from_date to end_date.
        """
        self.from_date = date(2011, 8, 1)
        self.end_date = date(2011, 8, 14)
        self.retrived_rows = self.reader.appointmentRows(self.test_dict, self.from_date, self.end_date)
        self.assertEquals(len(self.retrived_rows), 3)
        self.assertEqual(self.retrived_rows[1], self.test_dict[1])
        self.assertEqual(self.retrived_rows[2], self.test_dict[2]) 
        self.assertEqual(self.retrived_rows[3], self.test_dict[3])      
      
    def test_date_object_creator(self):
        """Convert date string to datetime object. """
        self.valid_dates = ['21/08/2011', '31/8/2011',]
        self.curr_date = self.reader.dateObjectCreator('1/8/2011')
        self.assertTrue(self.curr_date)
                           
    def test_database_record(self):
        """Convert worksheet row contents to proper types."""
        self.test_row = {
                            'appointmentdate1': '02/09/2011', 'fileno': '63601',
                            'appointmentstatus1': 'Scheduled', 'phonenumber': '969577542',
        }
        self.modified_row = self.reader.databaseRecord(self.test_row)
        self.app_date = self.modified_row['appointmentdate1']
        self.app_status = self.modified_row['appointmentstatus1']
        self.file_no = self.modified_row['fileno']
        self.phone = self.modified_row['phonenumber']
        
        
        #test if the fields where converted correctly
        self.assertEquals(self.app_date, date(2011, 9, 2))
        self.assertEquals(self.app_status, self.test_row['appointmentstatus1'])
        self.assertEquals(self.file_no, '63601')
        self.assertEquals(self.phone, 969577542)
        
        
        #test if the received fields are equal to those sent
        self.app_date = str(self.app_date)
        self.app_date = self.reader.dateFormat(self.app_date)
        self.assertEquals(self.app_date, self.test_row['appointmentdate1'])
        self.app_status = str(self.app_status)
        self.assertEquals(self.app_status, self.test_row['appointmentstatus1'])
        self.file_no = str(self.file_no)
        self.assertEquals(self.file_no, self.test_row['fileno'])
        self.phone = str(self.phone)
        self.assertEquals(self.phone, self.test_row['phonenumber'])
        
    def test_run_enrollment_check(self):
        """Tests if the patient has enrolled """
        self.enrol = self.reader.RunEnrollmentCheck(self.spreadsheet, 63601, self.start, self.until)
        self.assertEquals(self.enrol, True)
        
    def test_not_enrolled(self):
        """Test for a patient that is not enrolled. """
        self.not_enrol = self.reader.RunEnrollmentCheck(self.spreadsheet, 60001, self.start, self.until)
        self.assertEquals(self.not_enrol, False)
        
    def test_run_appointment_check(self):
        """Test if the appointments worksheets are retrieved."""
        self.month = self.reader.RunAppointment(self.spreadsheet, self.start, self.until)
        self.assertTrue(self.month)    
            
   