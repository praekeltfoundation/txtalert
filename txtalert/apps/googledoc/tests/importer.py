from django.test import TestCase
from django.contrib.auth.models import User
from txtalert.apps.googledoc.models import SpreadSheet
from txtalert.apps.googledoc.importer import Importer
from txtalert.apps.googledoc.reader.spreadsheetReader import SimpleCRUD
from txtalert.core.models import Patient, MSISDN, Visit, Clinic
from txtalert.apps.googledoc.tests.utils import (PatientUpdate, Appointment)
from datetime import datetime, timedelta, date
import random
import logging
import iso8601

class spreadsheet_tester(TestCase):
    """Testing the google spreadsheet import loop"""
    
    fixtures = ['patients', 'clinics']
    
    def setUp(self):
        self.importer = Importer()
        # make sure we're actually testing some data
        self.assertTrue(Patient.objects.count() > 0)
        self.email = 'olwethu@byteorbit'
        self.password = 'password' 
        self.spreadsheet, self.created = SpreadSheet.objects.get_or_create(spreadsheet='ByteOrbit copy of WrHI spreadsheet for Praekelt TxtAlert')
        #check if the spreadsheet was found in the database
        self.assertTrue(self.spreadsheet)
        #check if the spreadsheet is created if not in the database
        self.assertTrue(self.created)
    
    def tearDown(self):
        pass
    
    def test_import_spread_sheet(self):
        self.reader = SimpleCRUD(self.email, self.password)
        (self.month, self.enrol) = self.reader.Run(self.spreadsheet)
        self.assertTrue(self.month)
        self.assertTrue(self.enrol)
        
            
    def test_updatePatients(self):
       month = {0: {'appointmentdate1': datetime.date(2011, 8, 1), 'fileno': 1932, 'appointmentstatus1': 'Missed', 'phonenumber': 722155931},
                1: {'appointmentdate1': datetime.date(2011, 8, 10), 'fileno': 1663, 'appointmentstatus1': 'Scheduled', 'phonenumber': 794950510}, 
                2: {'appointmentdate1': datetime.date(2011, 8, 10), 'fileno': 1014, 'appointmentstatus1': 'Scheduled', 'phonenumber': 711520322}}
       
       
        
        
        
        
        
        