from django.test import TestCase
from django.contrib.auth.models import User
from txtalert.apps.googledoc.models import SpreadSheet
from txtalert.apps.googledoc.importer import Importer
from txtalert.apps.googledoc.reader.spreadsheetReader import SimpleCRUD
from txtalert.core.models import Patient, MSISDN, Visit, Clinic
from datetime import datetime, timedelta, date
import random
import logging
import iso8601

class spreadsheet_tester(TestCase):
    """Testing the google spreadsheet import loop"""
    
    fixtures = ['patients', 'clinics']
    
    def setUp(self):
        self.email = 'olwethu@byteorbit.com'
        self.password = 'password'
        self.importer = Importer(self.email, self.password)
        self.reader = SimpleCRUD(self.email, self.password)
        # make sure we're actually testing some data
        self.assertTrue(Patient.objects.count() > 0) 
        self.spreadsheet, self.created = SpreadSheet.objects.get_or_create(spreadsheet='spreadsheet for Praekelt TxtAlert')
        #check if the spreadsheet was found in the database
        self.assertTrue(self.spreadsheet)
        #check if the spreadsheet is created if not in the database
        self.assertTrue(self.created)
         self.month_worksheet = { 
                                     0: {'appointmentdate1': datetime.date(2011, 8, 1), 'fileno': 1932, 'appointmentstatus1': 'Missed', 'phonenumber': 722155931}, 
                                     1: {'appointmentdate1': datetime.date(2011, 8, 10), 'fileno': 1663, 'appointmentstatus1': 'Scheduled', 'phonenumber': 794950510},
                                     2: {'appointmentdate1': datetime.date(2011, 8, 10), 'fileno': 1014, 'appointmentstatus1': 'Scheduled', 'phonenumber': 711520322}, 
                                     3: {'appointmentdate1': datetime.date(2011, 8, 22), 'fileno': 2825, 'appointmentstatus1': 'Scheduled', 'phonenumber': 787048923},
                                     4: {'appointmentdate1': datetime.date(2011, 8, 10), 'fileno': 1135, 'appointmentstatus1': 'Scheduled', 'phonenumber': 730032293},
                                     5: {'appointmentdate1': datetime.date(2011, 8, 10), 'fileno': 2920, 'appointmentstatus1': 'Scheduled', 'phonenumber': 849616892},
                                     6: {'appointmentdate1': datetime.date(2011, 8, 10), 'fileno': 196, 'appointmentstatus1': 'Scheduled', 'phonenumber': 730772079} 
                        }

    
    def tearDown(self):
        pass
    
    def test_import_spread_sheet(self):
        self.start = date(2011, 8, 10)
        self.until = date(2011, 8, 10)
        self.month = self.reader.RunAppointment('ByteOrbit copy of WrHI spreadsheet for Praekelt TxtAlert', 'appointment worksheet', self.start, self.until)
        self.enrol = self.reader.RunEnrollmentCheck('ByteOrbit copy of WrHI spreadsheet for Praekelt TxtAlert', 'enrollment worksheet', 1932, self.start, self.until)
        self.assertTrue(self.month)
        self.assertTrue(self.enrol)
        #self.importer.updatePateints(self, patient_row, row):
        #row_no = row
            
    
    def test_updatePatients(self):
        
       
       

class SpreadSheetReaderTestCase(TestCase):
    
    def setUp(self):
        self.email = 'olwethu@byteorbit.com'
        self.password = 'password'
        self.start = date(2011, 8, 10)
        self.until = date(2011, 8, 10)
        self.reader = SimpleCRUD(self.email, self.password)
        self.assertTrue(self.reader) 
        self.start = date(2011, 8, 10)
        self.until = date(2011, 8, 10)
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
        self.month = self.reader.RunAppointment('ByteOrbit copy of WrHI spreadsheet for Praekelt TxtAlert', 'appointment worksheet', self.start, self.until)
        self.assertEquals(len(self.month), 20)   
       
    def test_RunEnrollmentCheck(self):
        self.enrol = self.reader.RunEnrollmentCheck('ByteOrbit copy of WrHI spreadsheet for Praekelt TxtAlert', 'enrollment worksheet', 1932, self.start, self.until)
        self.assertTrue(self.enrol)
        
                
        
        
        
        
        