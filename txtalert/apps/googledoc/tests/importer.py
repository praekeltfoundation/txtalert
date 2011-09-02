from django.test import TestCase
from django.contrib.auth.models import User
from txtalert.apps.googledoc.models import SpreadSheet, GoogleAccount
from txtalert.apps.googledoc.importer import Importer
from txtalert.apps.googledoc.reader.spreadsheetReader import SimpleCRUD
from txtalert.core.models import Patient, MSISDN, Visit, Clinic
from datetime import datetime, timedelta, date
import random


class ImporterTestCase(TestCase):
    """Testing the google spreadsheet import loop"""

    fixtures = ['patient', 'visit', 'clinic']

    def setUp(self):
        #dummy google login details
        self.email = 'txtalert@byteorbit.com'
        self.password = 'testtest'
        self.spreadsheet = 'Praekelt'
        self.empty_spreadsheet = 'Empty Spreadsheet'
        self.start = date.today() - timedelta(days=14)
        self.until = date.today()
        self.user = User.objects.all()[0]
        self.importer = Importer(self.user, self.email, self.password)
        # make sure we're actually testing some data
        self.assertTrue(Patient.objects.count() > 0)
        self.assertTrue(Visit.objects.count() > 0)
        self.assertTrue(Clinic.objects.count() > 0)
        self.enrolled_patients = {
                                    1: {
                                         'appointmentdate1': date(2011, 8, 1),
                                         'fileno': 1111111,
                                         'appointmentstatus1': 'Missed',
                                         'phonenumber': 999999999
                                        },
                                    2: {
                                         'appointmentdate1': date(2011, 8, 10),
                                         'fileno': 9999999,
                                         'appointmentstatus1': 'Attended',
                                         'phonenumber': 111111111
                                        }
        }

    def tearDown(self):
        pass

    def test_incorrect_spreadsheet_name(self):
        """Test for import with no existing spreadsheet names."""
        #invalid spreadsheet names
        self.doc_names = [
                             '##hgh', 'copy of appointment',
                             '123456', 123456, '#Praekelt'
        ]
        #rondomly select an invalid spreadsheet name
        self.invalid_doc_name = random.choice(self.doc_names)
        self.test_doc_name, self.correct = self.importer.import_spread_sheet(
                                self.invalid_doc_name, self.start, self.until
        )
        self.str_invalid_doc_name = str(self.invalid_doc_name)
        self.assertEquals(self.test_doc_name, self.str_invalid_doc_name)
        self.assertIs(self.correct, False)

    def test_empty_worksheets(self):
        """Test for a spreadsheet with no data to update."""
        self.doc_name, self.data = self.importer.import_spread_sheet(
                               self.empty_spreadsheet, self.start, self.until
        )
        self.assertEquals(self.doc_name, self.empty_spreadsheet)
        self.assertIs(self.data, False)

    def test_import_worksheets(self):
        """Test for importing worksheets from a spreadsheet."""
        self.from_date = date(2011, 7, 18)
        self.to_date = date(2011, 9, 22)
        self.enrolled, self.updates = self.importer.import_spread_sheet(
                             self.spreadsheet, self.from_date, self.to_date
        )
        self.assertEquals(self.enrolled, self.updates)

    def test_check_file_no_format_fail(self):
        """Test invalid file number format."""
        #invalid file number formats
        self.file_numbers = ['+1234', '#ab789', 'abc8901@@', 'ab#12345']
        #random selection of invalid file numbers
        self.file_no_test = random.choice(self.file_numbers)
        self.file_no, self.file_format = self.importer.check_file_no_format(
                                                            self.file_no_test
        )
        self.assertEqual(self.file_no, self.file_no_test)
        self.assertEqual(self.file_format, False)

    def test_check_file_no_pass(self):
        """Test file number format can only be alphanumeric."""
        #invalid file number formats
        self.file_numbers = [1234, 'ab789', 'abc8901', 'ab12345']
        #random selection of invalid file numbers
        self.file_no_test = random.choice(self.file_numbers)
        self.file_no, self.file_format = self.importer.check_file_no_format(
                                                      self.file_no_test
        )
        self.test_file_no = str(self.file_no_test)
        self.assertEqual(self.file_no,  self.test_file_no)
        self.assertEqual(self.file_format, True)

    def test_check_msisdn_format_fail(self):
        """Test for an invalid msisdn format."""
        #invalid phone number formats
        self.phones = [
                          1234567, 123456789012, '+1234567',
                          '012456789', '-12345678901', '###12345',
                          'abcdefghi', '12345abcd'
        ]
        #random selection of invalid phone numbers
        self.phone_test = random.choice(self.phones)
        #phone number and format correct flag
        self.phone, self.phone_format = self.importer.check_msisdn_format(
                                                           self.phone_test
        )
        self.assertIs(self.phone_format, False)
        self.assertEquals(self.phone_test, self.phone)

    def test_check_msisdn_format_pass(self):
        """Test for valid msisdn formats. """
        #valid phone numbers
        self.valid_phones = [
                                123456789, '0123456789',
                                27123456789, '+27123456789'
        ]
        #random selection of valid msisdn
        self.valid_phone = random.choice(self.valid_phones)
        #phone number and format correct flag
        self.phone, self.phone_format = self.importer.check_msisdn_format(
                                                              self.valid_phone
        )
        self.assertIs(self.phone_format, True)

    def test_create_patient_pass(self):
        """Test if the patient was created."""
        self.new_patient = {
                               'appointmentdate1': date(2011, 10, 1),
                               'fileno': '10101011',
                               'appointmentstatus1': 'Scheduled',
                               'phonenumber': 190909090
        }
        self.row = 3
        self.created = self.importer.create_patient(
                                self.new_patient, self.row, self.spreadsheet
        )
        self.assertIs(self.created, True)

    def test_create_patient_fail(self):
        """Test if the patient was not created. """
        self.new_patient = {
                               'appointmentdate1': date(2011, 10, 1),
                               'fileno': '###s01011',
                               'appointmentstatus1': 'Scheduled',
                               'phonenumber': 190909090
        }
        self.row = 12
        self.created = self.importer.create_patient(
                                self.new_patient, self.row, self.spreadsheet
        )
        self.assertIs(self.created, False)

    def test_set_cache_enrollment_status_fail(self):
        """Test caching of patient that have not enrolled."""
        self.uncached_filenos = [111100, 323232, 666666, 'abc113', '123zxy']
        self.cache_fileno = random.choice(self.uncached_filenos)
        self.cached_enrolled = self.importer.set_cache_enrollement_status(
                 self.spreadsheet, self.cache_fileno, self.start, self.until
        )
        self.assertIs(self.cached_enrolled, False)

    def test_set_cache_enrollment_status_pass(self):
        """Test caching of patient that have enrolled."""
        self.uncached_filenos = [721003, 61201, 9999999, 118801]
        self.cache_fileno = random.choice(self.uncached_filenos)
        self.cached_enrolled = self.importer.set_cache_enrollement_status(
                  self.spreadsheet, self.cache_fileno, self.start, self.until
        )
        self.assertIs(self.cached_enrolled, True)

    def test_get_cache_enrollment_status(self):
        """Test if cached enrollement status was found."""
        self.uncached_filenos = [721003, 61201, 9999999, 118801]
        self.cache_fileno = random.choice(self.uncached_filenos)
        self.importer.set_cache_enrollement_status(
                    self.spreadsheet, self.cache_fileno, self.start, self.until
        )
        self.cached = self.importer.get_cache_enrollement_status(
                                                   self.cache_fileno
        )
        self.assertIs(self.cached, True)

    def test_update_patients(self):
        """Test if a worksheet of patients is updated successfully."""
        self.enrolled, self.updates = self.importer.update_patients(
                                    self.enrolled_patients, self.spreadsheet,
                                    self.start, self.until
        )
        self.assertEqual(self.enrolled, 2)
        self.assertEqual(self.updates, 2)

    def test_invalid_file_no_(self):
        """Test if the file no is invalid."""
        #invalid phone number formats
        self.files = ['+1234', '#ab789', 'abc8901@@', 'ab#12345']
        #random selection of invalid file numbers
        self.file_test = random.choice(self.files)
        self.patient_row = {
                                'appointmentdate1': date(2011, 8, 10),
                                'fileno': self.file_test,
                                'appointmentstatus1': 'Missed',
                                'phonenumber': 987654321
        }
        self.row_no = 2
        self.valid = self.importer.update_patient(
                               self.patient_row, self.row_no, self.spreadsheet
        )
        self.assertIs(self.valid, False)

    def test_invalid_patient_id(self):
        """Patient not on the database test if its created."""
        self.patient_row = {
                               'appointmentdate1': date(2011, 8, 10),
                               'fileno': 555555,
                               'appointmentstatus1': 'Missed',
                               'phonenumber': 987654321
        }
        self.row_no = 2
        self.exists = self.importer.update_patient(
                               self.patient_row, self.row_no, self.spreadsheet
        )
        self.assertEqual(self.exists, True)

    def test_successful_patient_update(self):
        """Test that a patient was successfully updated."""
        self.patient_row = {
                               'appointmentdate1': date(2011, 8, 9),
                               'fileno': 9999999,
                               'appointmentstatus1': 'Attended',
                               'phonenumber': 987654321
        }
        self.row_no = 2
        self.patient_updated = self.importer.update_patient(
                              self.patient_row, self.row_no, self.spreadsheet
        )
        self.assertEqual(self.patient_updated, True)

    def test_updated_msisdn(self):
        """Test that the phone number was updated."""
        self.msisdn = random.choice(range(111111111, 999999999, 123456))
        self.msisdn = '27' + str(self.msisdn)
        self.curr_patient = Patient.objects.get(te_id='9999999')
        self.assertTrue(self.curr_patient)
        self.phone, self.created = self.importer.update_msisdn(
                                         self.msisdn, self.curr_patient
        )
        self.assertIs(self.created, True)
        self.assertEquals(self.msisdn, self.phone)

    def test_msisdn_not_updated(self):
        """Test if incorrect phone number are not updated """
        self.msisdn = random.choice(range(1111111, 9999999, 12345))
        self.curr_patient = Patient.objects.get(te_id='9999999')
        self.assertTrue(self.curr_patient)
        self.phone, self.created = self.importer.update_msisdn(
                                        self.msisdn, self.curr_patient
        )
        self.phone = int(self.phone)
        self.assertIs(self.created, False)
        self.assertEqual(self.msisdn, self.phone)

    def test_invalid_visit_id(self):
        """Visit not on the database."""
        (self.app_status, self.app_date, self.visit_id, self.curr_patient) = (
            'Scheduled', date(2011, 8, 10), 'jjjjjjj', 
            Patient.objects.get(te_id='9999999')
        )
        original_count = Visit.objects.count()
        status = self.importer.update_appointment_status(
            self.spreadsheet, self.app_status, self.app_date, 
            self.curr_patient, self.visit_id)
        self.assertEqual(status, 's')
        self.assertEqual(Visit.objects.count(), original_count + 1)

    def test_update_not_needed(self):
        """Appointment status already updated."""
        (self.app_status, self.app_date, self.visit_id, self.curr_patient) = (
          'Scheduled', date(2011, 8, 10), '02-9999999', 
          Patient.objects.get(te_id='9999999')
        )
        self.updated = self.importer.update_appointment_status(
            self.spreadsheet, self.app_status, self.app_date, 
            self.curr_patient, self.visit_id)
        self.assertEquals(self.updated, True)

    def test_status_is_updated(self):
        """Checks that the status was updated"""
        (self.app_status, self.app_date, self.visit_id, self.curr_patient) = (
             'Missed', date(2011, 8, 10), '02-9999999',
             Patient.objects.get(te_id='9999999')
        )
        self.status_updated = self.importer.update_appointment_status(
            self.spreadsheet, self.app_status, self.app_date, 
            self.curr_patient, self.visit_id)
        self.assertEquals(self.status_updated, 'm')

    def test_status_not_updated(self):
        """Test that the update failed."""
        (self.app_status, self.app_date, self.visit_id, self.curr_patient) = (
            'Missed', date(2011, 8, 1), '02-9999999', 
            Patient.objects.get(te_id='9999999')
        )
        self.status_updated = self.importer.update_appointment_status(
            self.spreadsheet, self.app_status, self.app_date, 
            self.curr_patient, self.visit_id)
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
        self.retrived_rows = self.reader.appointment_rows(
                                self.test_dict, self.from_date, self.end_date
        )
        self.assertEquals(len(self.retrived_rows), 3)
        self.assertEqual(self.retrived_rows[1], self.test_dict[1])
        self.assertEqual(self.retrived_rows[2], self.test_dict[2])
        self.assertEqual(self.retrived_rows[3], self.test_dict[3])

    def test_date_object_creator(self):
        """Convert date string to datetime object. """
        self.valid_dates = ['21/08/2011', '31/8/2011']
        self.curr_date = self.reader.date_object_creator('1/8/2011')
        self.assertTrue(self.curr_date)

    def test_database_record(self):
        """Convert worksheet row contents to proper types."""
        self.test_row = {
                            'appointmentdate1': '02/09/2011',
                            'fileno': '63601',
                            'appointmentstatus1': 'Scheduled',
                            'phonenumber': '969577542',
        }
        self.modified_row = self.reader.database_record(self.test_row)
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
        self.app_date = self.reader.date_format(self.app_date)
        self.assertEquals(self.app_date, self.test_row['appointmentdate1'])
        self.app_status = str(self.app_status)
        self.assertEquals(self.app_status, self.test_row['appointmentstatus1'])
        self.file_no = str(self.file_no)
        self.assertEquals(self.file_no, self.test_row['fileno'])
        self.phone = str(self.phone)
        self.assertEquals(self.phone, self.test_row['phonenumber'])

    def test_run_enrollment_check(self):
        """Tests if the patient has enrolled """
        self.enrol = self.reader.run_enrollment_check(
                          self.spreadsheet, 63601, self.start, self.until
        )
        self.assertEquals(self.enrol, True)

    def test_not_enrolled(self):
        """Test for a patient that is not enrolled. """
        self.not_enrol = self.reader.run_enrollment_check(
                                self.spreadsheet, 60001, self.start, self.until
        )
        self.assertEquals(self.not_enrol, False)

    def test_run_appointment_check(self):
        """Test if the appointments worksheets are retrieved."""
        self.month = self.reader.run_appointment(
                                       self.spreadsheet, self.start, self.until
        )
        self.assertTrue(self.month)
