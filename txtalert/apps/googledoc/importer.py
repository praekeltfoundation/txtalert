from txtalert.apps.googledoc.reader.spreadsheetReader import SimpleCRUD
from txtalert.core.models import Patient, MSISDN, Visit

import re
import logging

MSISDNS_RE = re.compile(r'^([+]?(0|27)[0-9]{9}/?)+$')
PHONE_RE = re.compile(r'[0-9]{9}')
MSISDN_RE = re.compile(r'^([+?0][0-9]{9}/?)+$')
APPOINTMENT_ID_RE = re.compile(r'^[0-9]{2}-[0-9]{9}$')

class Importer(object):
    def __init__(self, email, password):
        '''
        @arguments:
        email: The user's google email account username.
        password: The user's google account password.
        
        Uses google account details to login to the user's account.
        The account details are used by the spreadsheet reader class
        to perfom a ProgrammaticLogin on the user's account for
        spreadsheet access.
        '''
        self.email = email
        self.password = password
        self.reader = SimpleCRUD(self.email, self.password)
        
        
    def import_spread_sheet(self, doc_name, start, until):
        """
        @arguments:
        doc_name: the name of spreadsheet to import data from.
        start: indicates the date to start import data from.
        until: indicates the date import data function must stop at.
        
        This reads data from a google spreadsheet.
        If the data to be read from a spreadsheet is from 
        two worksheets then each worksheet is stored on a 
        sparate dictionary. For two worksheet the self.month will have 
        two dictionaries. Patient updates are done for each worksheet.
        
        self.month: stores the complete spreadsheet(has worksheets(s))
        """
        self.start = start
        self.until = until
        self.doc_name = doc_name
        self.month = self.reader.RunAppointment(self.doc_name, start, until)
        #check if the month has two worksheets
        if len(self.month) == 2:
            #update user appointment info for each worksheet 
            for worksheet in self.month:
                #check that the spreadsheet has data to update
                if len(self.month[worksheet]) != 0:
                    self.updatePatients(self.month[worksheet], self.doc_name, start, until)
                else:
                    logging.exception("The are no patient's to update") 
                    return   
        else:
            #check that the spreadsheet has data to update
            if len(self.month[worksheet]) != 0:
                #call function to process the worksheet appointment data
                self.updatePatients(self.month, self.doc_name, start, until)
                return          
            
    def updatePatients(self, month_worksheet, doc_name, start, until):
        """
        @arguments:
        month_worksheet: store the current month's worksheet from spreadsheet.
        doc_name: the name of spreadsheet to import data from.
        start: indicates the date to start import data from.
        until: indicates the date import data function must stop at.
        
        The method loops through each patient row in the 
        worksheet, It gets the file no for the current patient
        and checks if the patient has enrolled to use appointment service.
        If patient was found in the enrollment worksheet then perfom updates
        else log error that the patient needs to be enrolled.
        """
 
        #loop through the worksheet and check which patient details need to be updated
        for patient in month_worksheet:
            print 'patient_row: %s\n' % month_worksheet[patient]
            file_no = month_worksheet[patient]['fileno']
            print 'file no insde updatePatients: %s\n' % file_no
            #check if the patient has enrolled
            if self.reader.RunEnrollmentCheck(doc_name, file_no, start, until) is True:
                self.updatePatient(month_worksheet[patient],patient)
                print 'file no was found now doing updates\n'
                #found = True
                #return found
            elif self.reader.RunEnrollmentCheck(doc_name, file_no, start, until) is False:
                logging.debug('Unable to make updates for patients')
                print 'file no was not found ERROR\n'
                    
    def updatePatient(self, patient_row, row):
        '''
        @rguments:
        patient_row: A row that contains a patients appointment info.
        row: The number of the row on the worksheet
        
        This method compares the contents of the patient row
        to what is in the database and 
        make the appropriate updates if they are needed.
        
        The method checks if the patient is on the database;
        uses the file no and row no combo as the te_id key.
        
        @returns:
        patient_update: indicates if all the updates made to a patient where successful.
        '''
        row_no = row
        file_no =  patient_row['fileno']  
           
    
        if row_no < 10:
            row_no = '0' + str(row_no)
            visit_id = str(row_no) + '-' + str(file_no)
        else:
            visit_id = str(row_no) + '-' + str(file_no)
            
        print 'inside updatePatient visit_id: %s\n' % visit_id
                
        phone = patient_row['phonenumber']
        app_date = patient_row['appointmentdate1']
        app_status = patient_row['appointmentstatus1']
            
        #try to get the current patient from the database
        try:
            #use patient's unique id and row number on spreadsheet to find the patient database record
            curr_patient = Patient.objects.get(te_id=visit_id)
        except Patient.DoesNotExist:
            #log error in import log
            logging.exception("The patient was not found in the database")
            return 
        
        #check if the user already exist in the system so that data can be updated
        if curr_patient:
            #call methon to do appointment status update
            app_update = self.updateAppointmentStatus(app_status, app_date, visit_id) 
            #call method to update phone number
            phone_update = self.updateMSISDN(phone, curr_patient)
            #check if no error occured during patient updated 
            if app_update and phone_update:
                patient_update = True            
                return  (patient_update)
            else:
                patient_update = False            
                return  (patient_update)            
     
    def updateMSISDN(self, msisdn, curr_patient):
        '''
        @rguments:
        msisdn: the phone number to be updated
        curr_patient: is the patient who's phone number is being updated.
        
        The method checks if the phone number is in the correct format.
        Correct format for msisdn is: 123456789 / 27123456789
        If format is correct retrive it from database if not found
        create one and add it to the patient msisdns field.
        
        stores phone number in 27123456789 in the database
        
        @returns:
        created: Indicate whether an phone number update occurred
        '''
        #ensure that the msisdn is a string and in the correct format
        msisdn = str(msisdn)
        msisdn = msisdn.lstrip('0')
        msisdn = msisdn.lstrip('+')
        
        if len(msisdn) == 9:
            #check if the user phone number is in the correct format
            match = PHONE_RE.match(msisdn)
            
        elif len(msisdn) == 10:
            #check if the user phone number is in the correct format
            match = MSISDN_RE.match(msisdn)
            
        elif len(msisdn) == 11:
            #check if the user phone number is in the correct format
            match = MSISDNS_RE.match(msisdn)
            
        print 'match: %s\n match.groups(): %s\n' % (match, match.group())
        if match:
            #get the phone number
            phone_number = match.group()
            #check if the MSISDN format is international if not make it
            if len(phone_number) == 9:
                phone_number = '27' + phone_number                
            print 'phone_number: %s\n' % phone_number
            #update the patient phone number
            msisdn, created = MSISDN.objects.get_or_create(msisdn=phone_number)
            
            #check if the phone number is not on the list of MSISDN add it
            if msisdn not in curr_patient.msisdns.all():
                curr_patient.msisdns.add(msisdn)         
        # if the msisdn does not have correct phone number format log error        
        else:
            logging.exception('Phone number is incorrect format for patient: %s' % curr_patient)
            return
            
        if created:
            logging.debug('Phone number update for patient: %s' %  curr_patient)
            return created
        elif not created:
            logging.debug('Phone number is still the same for patient: %s' % curr_patient) 
            return created
                   
    def updateAppointmentStatus(self, app_status, app_date, visit_id):
        """
        @rgument:
        app_status: appointment status.
        app_date: appointment date.
        visit_id: database unique identifier for the patient
        
        The method begins by checking if the patient has made an appointment.
        If apointment was made check that the date has not changed.
        If the date in worksheet is more than that in the database
        then the appointment has been rescheduled if it is equal
        to it check if the user has attended a re/scheduled appointment,
        if it was missed modify to missed.
        
        Use logging for error reports and debugging.
        
        @returns:
        updated: Flag that indicates whether the appointment status was updated.        
        """          
        try:
            #use patient's unique id and row number on spreadsheet to find the patient database record
            curr_patient = Visit.objects.get(te_visit_id=visit_id)
            #print 'Visit curr_patient try block: %s\n' % curr_patient
        except Visit.DoesNotExist:
            #log error in import log
            logging.exception("Cannot make visit appointment")
            return
        #check if the patient appointment status has not changed if true dont update
        if app_status == curr_patient.status:
            updated = True
            #print 'app_status == curr_patient.status is True thus no updates\n'
            return updated
        
        #check if the user already exist in the system so that data can be updated
        if curr_patient:
            #check if the appointment date is the same as the one stored on the database
            if curr_patient.date >= app_date:
                #print 'curr_patient.date == app_date: %s\n' % curr_patient.date
                #check if the user has attended the scheduled appointment    
                if app_status == 'Attended':
                    #if the appointment was scheduled or rescheduled transform it to attended
                    if curr_patient.status == 's' or curr_patient.status == 'r':
                        try:
                            curr_patient.status = 'a'
                            curr_patient.save()
                            logging.debug('Appointment status update for Patient %s' % curr_patient)
                            updated = True
                            return updated
                        except:
                            logging.exception("Appointment failed to update")  
                            updated = False
                            return updated
                         
            #check if the patient appointment date has pasted
            elif curr_patient.date <= app_date:
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
                        updated = True
                        return updated
                    except:
                        logging.exception("Appointment failed to update")
                        updated = False
                        return updated
                    
                #if the user has missed a scheduled or rescheduled appointment
                if app_status == 'Missed':
                    #print 'app_status == Missed \n'
                    if curr_patient.status == 's' or curr_patient.status == 'r':
                        #print 'curr_patient.status == s or curr_patient.status == r: %s\n' % curr_patient.status
                        #print 'curr_patient.status: %s\n' % curr_patient.status
                        try:
                            curr_patient.status = 'm'
                            curr_patient.save()
                            #print 'curr_patient.status: %s\n' % curr_patient.status
                            logging.debug('Appointment status update for Patient %s' % curr_patient)
                            updated = True
                            return updated
                        except:
                            logging.exception("Appointment failed to update")
                            updated = False
                            return updated                     