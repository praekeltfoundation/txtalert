from txtalert.apps.googledoc.reader.spreadsheetReader import SimpleCRUD
from txtalert.core.models import Patient, MSISDN, Visit, Clinic
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import IntegrityError
import re
import logging
import hashlib

MSISDNS_RE = re.compile(r'^([+]?(0|27)[0-9]{9}/?)+$')
PHONE_RE = re.compile(r'[0-9]{9}')
MSISDN_RE = re.compile(r'^([+?0][0-9]{9}/?)+$')
FILE_NO = re.compile(r'^[a-zA-Z0-9]+$')
STATUS_RE = re.compile(r'^[a-zA-Z]+$')

#the amount of time to cache a enrollment status
CACHE_TIMEOUT = 30


class Importer(object):
    def __init__(self, owner, email, password):
        '''
        @arguments:
        email: The user's google email account username.
        password: The user's google account password.

        Uses google account details to login to the user's account.
        The account details are used by the spreadsheet reader class
        to perfom a ProgrammaticLogin on the user's account for
        spreadsheet access.
        '''
        self.owner = owner
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
        self.doc_name = str(doc_name)
        self.month = self.reader.run_appointment(self.doc_name, start, until)
        #counts how many enrolled patients where updated correctly
        correct_updates = 0
        #counter for number of patients found on the enrollement worksheet
        enrolled_counter = 0
        #check if a worksheet was returned
        if self.month == False:
            logging.exception("Incorrect spreadsheet or worksheet name")
            #indicates if the spreadsheet name was found in the database
            valid_name = False
            #return the name of invalid spreadsheet and the flag
            return (self.doc_name, valid_name)
        #if spreadsheet was found check if it has more than one worksheet
        else:
            if len(self.month) > 0:
                #loop through the worksheets in the spreadsheet
                for worksheet in self.month:
                    #check that the spreadsheet has data to update
                    if len(self.month[worksheet]) != 0:
                        #if true do update each enrolled patient
                        enrolled_counter, correct_updates = self.update_patients(
                            self.month[worksheet], self.doc_name, start, until
                        )
                        #return enrolled and updated counters
                        return enrolled_counter, correct_updates
                    #if the worksheet does not have data dont do updates
                    else:
                        logging.exception("The are no patient's to update")
                        #flag for checking if the spreadsheet has data
                        data = False
                        #return empty spreadsheet name and flag
                        return enrolled_counter, correct_updates
            else:
                logging.exception("The spreadsheet is empty.")
                data = False
                return (self.doc_name, data)

    def update_patients(self, month_worksheet, doc_name, start, until):
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
        #counts how many enrolled patients where updated correctly
        correct_updates = 0
        #counter for number of patients found on the enrollement worksheet
        enrolled_counter = 0
        #loop for checking which patient details need to be updated
        for patient in month_worksheet:
            file_no = month_worksheet[patient]['fileno']
            #call method to get the cached enrollemnt status for the patient
            enrolled = self.get_cache_enrollement_status(doc_name, file_no)
            #check if the cache has the patient's enrollment status
            if enrolled:
                logging.debug("Patient's enrollment status cached")
                #check if the patient was enrolled
                if enrolled == True:
                    logging.debug("Patient: %s status is True" % file_no)
                    #update the patient
                    update_flag = self.update_patient(
                                    month_worksheet[patient],
                                    patient, doc_name, start, until
                    )
                    enrolled_counter = enrolled_counter + 1
                    if update_flag == True:
                        correct_updates = correct_updates + 1
                        logging.debug(
                            "Cached enrollment status for patient: %s" %
                            file_no
                        )

                #check if patient needs to enroll
                elif enrolled is False:
                    logging.exception(
                    'Patient: %s cannot update with cached enrollment status' %
                    file_no
                    )
            #cache patient's appointment status if it was not cached.
            else:
                #call method to set cache
                cache_status = self.set_cache_enrollement_status(
                                           doc_name, file_no, start, until
                )
                #check if the patient is enrolled
                if cache_status == True:
                    #add to the enrolled patient counter
                    enrolled_counter = enrolled_counter + 1
                    #update enrolled patient
                    update_flag = self.update_patient(
                                    month_worksheet[patient],
                                    patient, doc_name, start, until
                    )
                    if update_flag == True:
                        correct_updates = correct_updates + 1
                        logging.debug("Updating the patient: %s" % file_no)
                #else, patient not enrolled
                else:
                    logging.exception('Cannot send reminder to Patient %s '
                        'since she/he has not been enrolled' % (file_no,))

        return (enrolled_counter, correct_updates)

    def cache_key(self, *args):
        return hashlib.md5(''.join(args)).hexdigest()

    def set_cache_enrollement_status(self, doc_name, file_no, start, until):
         #check if the patient has enrolled
        if self.reader.run_enrollment_check(doc_name, file_no,
                                            start, until) is True:
            #cache the enrollment check
            cache.set(self.cache_key(doc_name, file_no), True, CACHE_TIMEOUT)
            logging.debug("Caching True status for patient: %s" %
                           file_no
            )
            #the patient is enrolled, cache true for enrollement status
            enrolled_cache = True
            return enrolled_cache
        elif self.reader.run_enrollment_check(doc_name, file_no,
                                              start, until) is False:
            #cache the enrollment check
            cache.set(self.cache_key(doc_name, file_no), False, CACHE_TIMEOUT)
            #the patient is not enrolled, cache False for enrollement status
            enrolled_cache = False
            return enrolled_cache

    def get_cache_enrollement_status(self, doc_name, file_no):
        #check if the enrollment check was cached
        enrolled = cache.get(self.cache_key(doc_name, file_no))
        return enrolled

    def update_patient(self, patient_row, row, doc_name, start, until):
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
        patient_update: successful updates flag.
        '''
        #check that the arguments are proper types
        if type(row) == int and type(patient_row) == dict:
            row_no = row
            #get the contents of the row
            file_no, file_format = self.check_file_no_format(
                                                         patient_row['fileno']
            )
            phone, phone_format = self.check_msisdn_format(
                                                    patient_row['phonenumber']
            )
            app_date = patient_row['appointmentdate1']
            app_status, status_format = self.check_appointment_status(
                                            patient_row['appointmentstatus1']
            )
        #check if the data to be updated is in the correct formats
        if file_format and phone_format and status_format:
            if row_no < 10:
                row_no = '0' + str(row_no)
                visit_id = str(row_no) + '-' + file_no
            else:
                visit_id = str(row_no) + '-' + file_no

            #try to get the current patient from the database
            try:
                #try to locate the patient on the database
                curr_patient = Patient.objects.get(te_id=file_no)
            except Patient.DoesNotExist:
                #log error in import log
                logging.debug("Patient: %s not found in database" % file_no)
                #create a new patient
                created = self.create_patient(
                                             patient_row, row_no, doc_name,
                                             start, until
                )
                return created

            #if patient exist perform update and appointment date is valid
            if curr_patient:
                #get or create a clinic
                clinic = self.get_or_create_clinic(doc_name)
                #call method to do appointment status update
                app_update = self.update_appointment_status(
                        app_status, curr_patient, app_date, visit_id, clinic
                )
                #call method to update phone number
                phone_update = self.update_msisdn(phone, curr_patient)
                #check if no error occured during patient updated
                if app_update or phone_update:
                    patient_update = True
                    return  (patient_update)
                else:
                    patient_update = False
                    return  (patient_update)
        #if any of the format are incorrect dont update patient
        else:
            logging.exception("Invalid date format for patient: %s" % file_no)
            patient_update = False
            return patient_update

    def check_appointment_status(self, status):
        status_format = False
        status_options = ['missed', 'scheduled', 'attended', 'rescheduled']
        #check if the status is a string
        try:
            #check if the correct format
            match = STATUS_RE.match(status)
            try:
                #return the string to check
                app_status = match.group()
                app_status = app_status.lower()
                #check if the status is in the valid options list
                for valid_status in status_options:
                    #check if the status is valid
                    if valid_status == app_status:
                        status_format = True
            except AttributeError:
                logging.exception("Appointment status invalid format")
        except TypeError:
            logging.exception("Appointment status is not characters")

        return (status, status_format)

    def check_file_no_format(self, file_number):
        #ensure the file number is a string type
        file_no = str(file_number)
        #check the format of the file number
        try:
            #check file number format
            match = FILE_NO.match(file_no)
            if match is None:
                # No match, it isn't in the correct format.
                logging.exception("Patient %s is not in the correct format. "
                    "Only letters and digits are allowed." % (file_no,))
                return (file_number, False)
            try:
                #get string that matched pattern
                file_no = match.group()
                correct_format = True
                #return the correct file number
                return (file_no, correct_format)
            except AttributeError:
                logging.exception(
                     "File number can be combination of numbers and characters"
                )
                correct_format = False
                return (file_number, correct_format)
        except TypeError:
            logging.exception(
                     "File number can be combination of numbers and characters"
            )
            correct_format = False
            return (file_number, correct_format)

    def check_msisdn_format(self, phone):
        msisdn = str(phone)
        msisdn = msisdn.lstrip('0')
        msisdn = msisdn.lstrip('+')
        #check if the phone is the correct format
        if len(msisdn) == 9:
            try:
                #check if the user phone number is in the correct format
                match = PHONE_RE.match(msisdn)
                try:
                    #get the phone number
                    phone_number = match.group()
                    correct_format = True
                    phone_number = '27' + phone_number
                    return (phone_number, correct_format)
                except AttributeError:
                    logging.exception("invalid msisdn format.")
                    updated = False
                    return (phone, updated)
            except TypeError:
                logging.exception("The phone number must be in string format")
                phone_update = False
                return (phone, phone_update)
        #check if the phone is in internation format
        elif len(msisdn) == 11:
            try:
                #check if the user phone number is in the correct format
                match = MSISDNS_RE.match(msisdn)
                try:
                    #get the phone number
                    phone_number = match.group()
                    correct_format = True
                    return (phone_number, correct_format)
                except AttributeError:
                    logging.exception("invalid msisdn format.")
                    updated = False
                    return (phone, updated)
            except TypeError:
                logging.exception("The phone number must be in string format")
                phone_update = False
                return (phone, phone_update)
        else:
            logging.exception("The phone number must be 9 to 11 digits")
            phone_update = False
            return (phone, phone_update)

    def create_patient(self, patient_row, row_no, doc_name, start, until):
        #get the contents of the row
        file_no, file_format = self.check_file_no_format(patient_row['fileno'])
        phone, phone_format = self.check_msisdn_format(
                                                patient_row['phonenumber']
        )
        app_date = patient_row['appointmentdate1']
        app_status = patient_row['appointmentstatus1']
        #check if the file number is correct format
        if file_format:
            #visit id
            if row_no < 10:
                row_no = '0' + str(row_no)
                visit_id = str(row_no) + '-' + file_no
            else:
                visit_id = str(row_no) + '-' + file_no
            #get the owner
            # owner = self.get_or_create_owner('googledoc')
            #if phone format is valid create patient's msisdn
            if phone_format:
                #create or get phone number
                msisdn, msisdn_created = self.get_or_create_msisdn(phone)
            #check if the patient field are valid formats
            if self.owner and msisdn and file_no:
                #try to create a patient with the contents of the worksheet row
                try:
                    #create a new patient
                    new_patient = Patient(
                                              te_id=file_no,
                                              active_msisdn=msisdn,
                                              owner=self.owner
                    )
                    #save to database
                    new_patient.save()
                    patient_created = True
                    # add msisdn to list of msisdns
                    new_patient.msisdns.add(msisdn)
                    #get or create a clinic
                    clinic = self.get_or_create_clinic(doc_name)
                    enrolled = self.set_cache_enrollement_status(
                                    doc_name, file_no, start, until
                    )
                    #check if the enrollment check was cached
                    enrolled = cache.get(file_no)
                    #convert string enroment to a choice key used in database
                    status = self.update_needed(app_status)
                    #if patient is enrolled create a visit instanceprint
                    if enrolled and patient_created and clinic:
                        #call method to create a visit for the new patient
                        visit, visit_created = self.create_visit(
                                                    visit_id, new_patient,
                                                    app_date, status, clinic
                        )
                        if visit_created:
                            #indicate that patient and visit was created
                            created = True
                            logging.debug("Created patient's visit")
                            return created
                    elif not enrolled:
                        #the patient was created and erollment status is false
                        return patient_created
                #catch relational integrity error
                except IntegrityError:
                    logging.exception("Failed to create patient invalid field")
                    patient_created = False
                    return patient_created
        #if any of the patient data was incorrect dont create patient
        else:
            logging.debug("Error creating patient with invalid file number")
            #indicate that patient could not be created becuase of the error
            created = False
            return created

    def create_visit(self, visit_id, new_patient, app_date, status, clinic):
        #use spreadsheet data to create visit
        try:
            #create a the visit
            new_visit = Visit(
                                 te_visit_id=visit_id,
                                 patient=new_patient,
                                 date=app_date,
                                 status=status,
                                 clinic=clinic
            )
            new_visit.save()
            logging.debug("Created the visit %s for new patien" % visit_id)
            visit_created = True
            visit = new_visit
        except IntegrityError:
            logging.exception("Failed to create visit %s." % visit_id)
            visit_created = False
            visit = None
        return (visit, visit_created)

    def get_or_create_clinic(self, doc_name):
        #get or create a clinic with the name of the spreadsheet
        clinic, created = Clinic.objects.get_or_create(name=doc_name,
            user=self.owner)
        return clinic

    def get_or_create_owner(self, name):
         #get the user or create one
        owner, owner_created = User.objects.get_or_create(username=name)
        return owner

    def get_or_create_msisdn(self, phone):
        #create a msisdn
        msisdn, msisdn_created = MSISDN.objects.get_or_create(msisdn=phone)
        return (msisdn, msisdn_created)

    def update_msisdn(self, msisdn, curr_patient):
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
        phone, phone_format = self.check_msisdn_format(msisdn)
        if phone_format is True:
            #update the patient phone number
            phone, created = MSISDN.objects.get_or_create(msisdn=msisdn)
            if created:
                #check if the phone number is not on the list of MSISDN add it
                if phone not in curr_patient.msisdns.all():
                    curr_patient.msisdns.add(phone)
                    #set the patient's active msisdn to recently added msisdn
                    curr_patient.active_msisdn = phone
                logging.debug('Phone number update for patient: %s' %
                               curr_patient
                )
                return (phone.msisdn, created)
            elif not created:
                logging.debug('Phone number has not changed for patient: %s' %
                               curr_patient)
                return (phone.msisdn, created)
        # if the msisdn does not have correct phone number format log error
        else:
            logging.exception('invalid phone number format for patient: %s' %
                              curr_patient)
            phone_update = False
            return (msisdn, phone_update)

    def update_needed(self, status):
        """
        @rguments:
        status: appointment status.

        Converts the appointment status
        variable to the length of the
        one stored on the database.

        @returns:
        database_status: appointment status a letter.
        """

        if status == 'Missed':
            return 'm'
        elif status == 'Rescheduled':
            return 'r'
        elif status == 'Attended':
            return 'a'
        elif status == 'Scheduled':
            return 's'

    def update_appointment_status(self, app_status, new_patient,
                                  app_date, visit_id, clinic_name):
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
        updated: indicates whether the appointment status was updated.
        """
        #converts a string enroment to a choice key used in database
        status = self.update_needed(app_status)
        try:
            #get patient's visit instance
            curr_visit = Visit.objects.get(te_visit_id=visit_id)
        except Visit.DoesNotExist:
            #log error in import log
            logging.debug("Creating a new visit for patient")
            if type(clinic_name) == str:
                clinic = self.get_or_create_clinic(clinic_name)
            else:
                clinic = clinic_name
            curr_visit, visit_created = self.create_visit(
                                                  visit_id, new_patient,
                                                  app_date, status, clinic
            )
            #check if the visit was created
            if not visit_created:
                return status

        #stores variable used to check if appointment updates are needed
        progress = self.update_needed(app_status)
        #dont update if the status has not changed
        if progress == curr_visit.status:
            logging.debug("The appointment status does not require an update")
            return status

        #if visit exist update to current status
        if curr_visit:
            #if appointment date is coming or is now update status
            if curr_visit.date >= app_date:
                #check if the user has attended the scheduled appointment
                if app_status == 'Attended':
                    #check if it was scheduled or rescheduled
                    if curr_visit.status == 's' or curr_visit.status == 'r':
                        #if true change to attended
                        try:
                            #save new appointment status
                            curr_visit.status = 'a'
                            curr_visit.save()
                            logging.debug('Patient %s attended appointment' %
                                          visit_id)
                            return curr_visit.status
                        #except save fial
                        except IntegrityError:
                            logging.exception("Appointment failed to update")
                            return curr_visit.status

                #if the user has missed a scheduled or rescheduled appointment
                if app_status == 'Missed':
                    if curr_visit.status == 's' or curr_visit.status == 'r':
                        try:
                            curr_visit.status = 'm'
                            curr_visit.save()
                            logging.debug('Patient missed appointment %s' %
                                          visit_id)
                            return curr_visit.status
                        except:
                            logging.exception("Appointment failed to update")
                            return curr_visit.status

            #check if the patient appointment date has passed
            elif curr_visit.date < app_date:
                #check if the patient has rescheduled
                if app_status == 'Rescheduled' and curr_visit.status == 's':
                    curr_visit.status = 'r'
                    try:
                        #change date to be the new rescheduled appointment date
                        curr_visit.date = app_date
                        curr_visit.save()
                        logging.debug('Patient %s rescheduled' % visit_id)
                        return curr_visit.status
                    except:
                        logging.exception("Appointment failed to update")
                        return curr_visit.status
