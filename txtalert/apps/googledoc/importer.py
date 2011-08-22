from django.db import IntegrityError
from txtalert.apps.googledoc.reader.spreadsheetReader import SimpleCRUD
from txtalert.core.models import Patient, MSISDN, Visit, Clinic

import iso8601
import re
import logging
from datetime import datetime, date

PATIENT_ID_RE = re.compile(r'^[0-9]{2}-[0-9]{5}$')
MSISDNS_RE = re.compile(r'^([+]?(0|27)[0-9]{9}/?)+$')
MSISDN_RE = re.compile(r'[0-9]{9}')
APPOINTMENT_ID_RE = re.compile(r'^[0-9]{2}-[0-9]{9}$')
DATE_RE = re.compile(r'^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{2}:[0-9]{2}:[0-9]{2}$')

class Importer(object):
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.reader = SimpleCRUD(self.email, self.password)
        
        
    def import_spread_sheet(self, doc_name, start, until):
        """Gets the name of the spreadsheet to be imported"""
        self.start = start
        self.until = until
        self.doc_name = doc_name
        self.month = self.reader.RunAppointment(self.doc_name, start, until)
        #call function to process the worksheet appointment data
        self.updatePatients(self.month, self.doc_name, start, until)
            
            
    def updatePatients(self, month_worksheet, doc_name, start, until):
        """Updates patients data if the patient exists."""
        #loop through the worksheet and check which patient details need to be updated
        for patient in month_worksheet:
            file_no = month_worksheet[patient]['fileno']
            print file_no
            #check if the patient has enrolled
            if self.reader.RunEnrollmentCheck(doc_name, file_no, start, until) is True:
                self.updatePatient(month_worksheet[patient], patient)
                #found = True
                #return found
            elif self.reader.RunEnrollmentCheck(doc_name, file_no, start, until) is False:
                logging.debug('Unable to make updates for patients')
                return
                #found = False
                #return found
                    
    def updatePatient(self, patient_row, row):
        row_no = row
        file_no =  patient_row['fileno']     
    
        if row_no < 10:
            row_no = '0' + str(row_no)
            visit_id = str(row_no) + '-' + str(file_no)
        else:
            visit_id = str(row_no) + '-' + str(file_no)
                
        phone = patient_row['phonenumber']
        app_date = patient_row['appointmentdate1']
        app_status = patient_row['appointmentstatus1']
            
        #try to get the current patient from the database
        try:
            #use patient's unique id and row number on spreadsheet to find the patient database record
            curr_patient = Patient.objects.get(te_id=visit_id)
        except Patient.DoesNotExist as perror:
            #log error in import log
            logging.exception(str(perror))
            return
            
                
        #try to get current patient visit
        try:
            curr_patient_visit = Visit.objects.get(te_visit_id=visit_id)
            
        except Visit.DoesNotExist as verror:
            #log error in import log
            logging.exception(str(verror))
            return
        
        #check if the user already exist in the system so that data can be updated
        if curr_patient:
            #call methon to do appointment status update
            self.updateAppointmentStatus(app_status, app_date, visit_id) 
            #call method to update phone number
            self.updateMSISDN(phone, curr_patient)
            return           
    
    
    
    def printP(self, p):
        mylist = []
        print p
        for i in p:
            print i.te_id
            mylist.append(i.te_id)
            
        return mylist
     
     
     
    def updateMSISDN(self, msisdn, curr_patient):
        #convert msisdn to string
        msisdn = str(msisdn)
        #check if the user phone number is in the correct format
        match = MSISDN_RE.match(msisdn)
        print 'match: %s\n match.groups(): %s\n' % (match, match.group())
        if match:
            #create MSISDN format
            phone_number = '27' + match.group()
            print 'phone_number: %s\n' % phone_number
            #update the patient phone number
            msisdn, created = MSISDN.objects.get_or_create(msisdn=phone_number)
            
            #check if the phone number is not on the list of MSISDN add it
            if msisdn not in curr_patient.msisdns.all():
                curr_patient.msisdns.add(msisdn)
                return 
                  
        else:
            logging.exception('Phone number is incorrect format for patient: %s' % curr_patient)
            return
            
        if created:
            logging.debug('Phone number update for patient: %s' %  curr_patient)
            return created
        elif not created:
            logging.debug('Phone number is still the same for patient: %s' % curr_patient) 
            return False
       
       
                   
    def updateAppointmentStatus(self, app_status, app_date, visit_id):
        """Updates the existing patient appointment information."""
        #print 'app_status at updateAppointmentStatus: %s\n' % app_status
        #print 'app_date at updateAppointmentStatus: %s\n' % app_date
        #print 'visit_id at updateAppointmentStatus: %s\n' % visit_id
           
        try:
            #use patient's unique id and row number on spreadsheet to find the patient database record
            curr_patient = Visit.objects.get(te_visit_id=visit_id)
            #print 'Visit curr_patient try block: %s\n' % curr_patient
        except Visit.DoesNotExist as verror:
            #log error in import log
            logging.exception(str(verror))
            return
        #check if the status has canged
        if app_status == curr_patient.status:
            #print 'app_status == curr_patient.status is True thus no updates\n'
            return
        
        #check if the user already exist in the system so that data can be updated
        if curr_patient:
            #check if the appointment date is the same as the one stored on the database
            if curr_patient.date == app_date:
                #print 'curr_patient.date == app_date: %s\n' % curr_patient.date
                #check if the user has attended the scheduled appointment    
                if app_status == 'Attended':
                    #if the appointment was scheduled or rescheduled transform it to attended
                    if curr_patient.status == 's' or curr_patient.status == 'r':
                        curr_patient.status = 'a'
                        try:
                            curr_patient.save()
                            logging.debug('Appointment status update for Patient %s' % curr_patient)
                            return
                        except ValidationError as verror:
                            logging.exception(str(verror))  
                            return
                            
                #if the user has missed a scheduled or rescheduled appointment
                if app_status == 'Missed':
                    #print 'app_status == Missed \n'
                    if curr_patient.status == 's' or curr_patient.status == 'r':
                        #print 'curr_patient.status == s or curr_patient.status == r: %s\n' % curr_patient.status
                        curr_patient.status = 'm'
                        #print 'curr_patient.status: %s\n' % curr_patient.status
                        try:
                            curr_patient.save()
                            #print 'curr_patient.status: %s\n' % curr_patient.status
                            logging.debug('Appointment status update for Patient %s' % curr_patient)
                            saved = True
                            return saved
                        except ValidationError as verror:
                            logging.exception(str(verror))
                            return         
                        
            #check if the patient appointment date has pasted
            elif curr_patient.date < app_date:
                #print 'curr_patient.date > app_date: %s\n' % curr_patient.date           
                #check if the patient has rescheduled 
                if app_status == 'Rescheduled' and curr_patient.status == 's':
                    print ''
                    curr_patient.status = 'r' 
                    try:
                        #change date to be the new rescheduled appointment date
                        curr_patient.date = app_date
                        curr_patient.save()
                        logging.debug('Appointment status update for Patient %s' % curr_patient)
                        return
                    except ValidationError as verror:
                        logging.exception(str(verror)) 
                        return             
        
         
    