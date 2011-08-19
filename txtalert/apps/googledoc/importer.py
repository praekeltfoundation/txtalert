from django.db import IntegrityError
from txtalert.apps.googledoc.reader.spreadsheetReader import SimpleCRUD
from txtalert.core.models import Patient, MSISDN, Visit, Clinic

import iso8601
import re
import logging
from datetime import datetime, date

PATIENT_ID_RE = re.compile(r'^[0-9]{2}-[0-9]{5}$')
MSISDNS_RE = re.compile(r'^([+]?(0|27)[0-9]{9}/?)+$')
MSISDN_RE = re.compile(r'[+]?(0|27)([0-9]{9})')
APPOINTMENT_ID_RE = re.compile(r'^[0-9]{2}-[0-9]{9}$')
DATE_RE = re.compile(r'^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{2}:[0-9]{2}:[0-9]{2}$')

class Importer(object):
    def __init__(self, uri=None, verbose=False):
        self.client = Client(uri, verbose)

    def import_spread_sheet(self, doc_name, start, until):
        """Gets the name of the spreadsheet to be imported"""
        self.start = start
        self.until = until
        self.doc_name = doc_name
        self.reader = SimpleCRUD(self.GOOGLE_USERNAME, self.GOOGLE_PASSWORD)
        month = self.reader.RunAppointment(self.doc_name, 'appointment worksheet', self.start, self.until)
        #check if the month has two worksheets
        if len(month) == 2:
            #update user appointment info for each worksheet 
            for worksheet in month:
               self.updatePatients(month_worksheet=month[worksheet])     
        else:
            #call function to process the worksheet appointment data
            self.updatePatients(month_worksheet=month)
            
            
    def updatePatients(self, month_worksheet):
        """Updates patients data if the patient exists."""
        #loop through the worksheet and check which patient details need to be updated
        for patient in month_worksheet:
            file_no = month_worksheet[patient]['fileno']
            #check if the patient has enrolled
            if self.reader.RunEnrollmentCheck(self.doc_name, 'enrollment worksheet', file_no) is True:
                self.updatePatient(month_worksheet[patient], patient)
            elif self.reader.RunEnrollmentCheck(self.doc_name, 'enrollment worksheet', file_no) is False:
                logging.debug('Unable to make updates for patient: %s , needs to enrol first' % curr_patient)
             
                    
    def updatePateints(self, patient_row, row):
        row_no = row
        file_no =  mpatient_row['fileno']
        
        if row_no < 10:
            row_no = '0' + str(row_no)
            visit_id = row_no + '-' + str(file_no)
        else:
            visit_id = str(row_no) + '-' + str(file_no)
                
        phone = month_worksheet[patient]['phonenumber']
        phone = '27' + str(phone)
        phone = int(phone)
        app_date = month_worksheet[patient]['appointmentdate1']
        app_status = month_worksheet[patient]['appointmentstatus1']
            
        #try to get the current patient from the database
        try:
            #use patient's unique id and row number on spreadsheet to find the patient database record
            curr_patient = Patient.objects.get(te_id=visit_id)
        except Patient.DoesNotExist as perror:
            #log error in import log
            logging.exception(str(perror))
                
        #try to get current patient visit
        try:
            curr_patient_visit = Visit.objects.get(te_visit_id=visit_id)
            
        except Visit.DoesNotExist as verror:
            #log error in import log
            logging.exception(str(verror))
        
         #check if the user already exist in the system so that data can be updated
        if curr_patient:
            #update the patient phone number
            msisdn, created = MSISDN.objects.get_or_create(msisdn=phone_number)
            if msisdn not in patient.msisdns.all():
                patient.msisdns.add(msisdn) 
            if created:
                logging.debug('Phone number update for patient: %s' %  curr_patient)
            if not created:
                logging.debug('Phone number is still the same for patient: %s' % curr_patient) 
                        
        #check if the patient's appointment date has changed
        if curr_patient_visit.date != app_date:
            curr_patient_visit.date = app_date
            try:
                curr_patient.save()
                logging.debug('Appointment date update for patient: %s' %  curr_patient)
            except ValidationError as verror:
                logging.exception('Failed to update Appointment date for patient: %s error is: %s' % (curr_patient, str(verror))) 

        #call methon to do appointment status update
        self.updateAppointmentStatus(app_status, visit_id)                      
                
                   
    def updateAppointmentStatus(app_status, visit_id):
        """Updates the existing patient appointment information."""
        try:
            #use patient's unique id and row number on spreadsheet to find the patient database record
            curr_patient = Visit.objects.get(te_visit_id=visit_id)
        except Visit.DoesNotExist as verror:
            #log error in import log
            logging.exception(str(verror))
            
       #check if the user already exist in the system so that data can be updated
        if curr_patient:
            #check if the user has attended the scheduled appointment    
            if app_status == 'Attended':
                #if the appointment was scheduled or rescheduled transform it to attened
                if curr_patient.status == 's' or curr_patient.status == 'r':
                    curr_patient.status = 'a'
                    try:
                        curr_patient.save()
                        logging.debug('Appointment status update for Patient %s' % curr_patient)
                    except ValidationError as verror:
                        logging.exception(str(verror))   
        
            #if the user has missed a scheduled or rescheduled appointment
            elif app_status == 'Missed':
                if curr_patient.status == 's' or curr_patient.status == 's':
                    curr_patient.status = 'm'
                    try:
                        curr_patient.save()
                        logging.debug('Appointment status update for Patient %s' % curr_patient)
                    except ValidationError as verror:
                        logging.exception(str(verror)) 
            
            #check if the patient has rescheduled 
            elif app_status = 'Rescheduled' and curr_patient.status == 's':
                curr_patient.status = 'r' 
                try:
                    curr_patient.save()
                    logging.debug('Appointment status update for Patient %s' % curr_patient)
                except ValidationError as verror:
                    logging.exception(str(verror))                  
                        
                        
            
         
    