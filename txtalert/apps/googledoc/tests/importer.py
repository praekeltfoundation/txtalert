from django.test import TestCase
from django.db import IntegrityError
from txtalert.apps.googledoc.models import SpreadSheet, GoogleAccount
from txtalert.apps.googledoc.importer import Importer
from txtalert.apps.googledoc.reader.spreadsheetReader import SimpleCRUD
from txtalert.core.models import Patient, MSISDN, Visit, Clinic
from datetime import datetime, timedelta, date
import logging

class Importer_tester(TestCase):
    """Testing the google spreadsheet import loop"""
    
    fixtures = ['patient', 'visit']
    
    def setUp(self):
        self.email = 'olwethu@byteorbit.com'
        self.password = 'password'
        self.spreadsheet = 'ByteOrbit copy of WrHI spreadsheet for Praekelt TxtAlert'
        self.importer = Importer(self.email, self.password)
        self.reader = SimpleCRUD(self.email, self.password)
        self.start = date.today() - timedelta(days=14) 
        self.until = date.today()
        # make sure we're actually testing some data
        self.assertTrue(Patient.objects.count() > 0)
        self.month_worksheet = { 
                                     1: {'appointmentdate1': date(2011, 8, 1), 'fileno': 1932, 'appointmentstatus1': 'Missed', 'phonenumber': 722155931}, 
                                     2: {'appointmentdate1': date(2011, 8, 10), 'fileno': 1663, 'appointmentstatus1': 'Scheduled', 'phonenumber': 794950510}, 
                        }

    def tearDown(self):
        pass
    
    
    def test_updatePatient(self):
        self.patient_row = {'appointmentdate1': date(2011, 8, 1), 'fileno': 1932, 'appointmentstatus1': 'Missed', 'phonenumber': 722155931}
        self.row = 01
        self.assertTrue(self.importer.updatePatient(self.patient_row, self.row))
        
    def test_updateMSISDN(self):
        self.msisdn = 27712491201
        self.curr_patient = Patient.objects.get(te_id='02-1663')
        self.assertTrue(self.curr_patient)
        self.created = self.importer.updateMSISDN(self.msisdn, self.curr_patient)
        print self.created
        self.assertIs(self.created, True)
       
    def test_updateAppointmentStatus(self):
        (self.app_status, self.app_date, self.visit_id) = ('Missed', date(2011, 9, 10), '02-1663')
        self.saved = self.importer.updateAppointmentStatus(self.app_status, self.app_date, self.visit_id)
        #self.assertIs(self.saved, True)
        self.assertTrue(self.saved)
    
    def test_import_spread_sheet(self):
        self.month = self.reader.RunAppointment(self.spreadsheet, self.start, self.until)
        self.enrol = self.reader.RunEnrollmentCheck(self.spreadsheet, 1663, self.start, self.until)
        self.assertTrue(self.month)
        self.assertTrue(self.enrol)
        #self.importer.updatePateints(self, patient_row, row):
        #row_no = row
            
    
    def test_updatePatients(self):
        self.tester = {2: {'appointmentdate1': date(2011, 8, 23), 'fileno': 1663, 'appointmentstatus1': 'Scheduled', 'phonenumber': 794950510}}
        self.assertTrue(self.importer.updatePatients(self.tester, self.spreadsheet, self.start, self.until))
        #(self.r , self.f) = self.importer.updatePatients(self.month_worksheet, self.spreadsheet, self.start, self.until)
        #self.assertEquals(self.r, 1)
        #self.assertEquals(self.f, 1663)
 
      
class SpreadSheetReaderTestCase(TestCase):
    
    def setUp(self):
        self.email = 'olwethu@byteorbit.com'
        self.password = 'password'
        self.spreadsheet = 'ByteOrbit copy of WrHI spreadsheet for Praekelt TxtAlert'
        self.reader = SimpleCRUD(self.email, self.password)
        self.assertTrue(self.reader) 
        self.start = date.today() - timedelta(days=14) 
        self.until = date.today()
        self.spreadsheet = 'ByteOrbit copy of WrHI spreadsheet for Praekelt TxtAlert'
        self.mydict = {         
                       1: {'appointmentdate1': '10/8/2011', 'fileno': '1663', 'appointmentstatus1': 'Scheduled', 'phonenumber': '794950510', 'appoinmentattenddate1': None},
                       2: {'appointmentdate1': '10/8/2011', 'fileno': '1014', 'appointmentstatus1': 'Scheduled', 'phonenumber': '711520322', 'appoinmentattenddate1': None}, 
                       3: {'appointmentdate1': '22/08/2011', 'fileno': '2825', 'appointmentstatus1': 'Scheduled', 'phonenumber': '787048923', 'appoinmentattenddate1': None},
                       4: {'appointmentdate1': '10/8/2011', 'fileno': '1135', 'appointmentstatus1': 'Scheduled', 'phonenumber': '730032293', 'appoinmentattenddate1': None}
                }
        
    def tearDown(self):
        pass
       
    def test_dateObjectCreator(self):
        self.curr_date = self.reader.dateObjectCreator('1/8/2011')
        self.assertTrue(self.curr_date)
        
    def test_databaseRecord(self):
        for k in self.mydict:
            self.proper_dict = self.reader.databaseRecord(self.mydict[k])
            self.assertTrue(self.proper_dict)
        
    def test_RunAppointment(self):
        self.month = self.reader.RunAppointment(self.spreadsheet, self.start, self.until)
        self.assertTrue(self.month)   
       
    def test_RunEnrollmentCheck(self):
        self.enrol = self.reader.RunEnrollmentCheck(self.spreadsheet, 1663, self.start, self.until)
        self.assertTrue(self.enrol)
        
                
        
        
        
        
        