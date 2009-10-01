"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from therapyedge.models import *
from bookingtool.models import *


def create_booking_patient():
    booking_patient = BookingPatient()
    
    booking_patient.name = 'name'
    booking_patient.surname = 'surname'
    
    booking_patient.te_id = '123456789'
    booking_patient.mrs_id = 'A1234567890-1'
    
    booking_patient.opt_status = 'not-yet'
    booking_patient.treatment_cycle = 1
    booking_patient.last_clinic = Clinic.objects.all()[0]
    booking_patient.age = 35
    return booking_patient

class BookingPatientTestCase(TestCase):
    
    fixtures = ['patients', 'clinics', 'visits', 'initial_data']
    
    def setUp(self):
        self.booking_patient = create_booking_patient()
    
    def tearDown(self):
        pass
    
    def test_appointment_inheritance(self):
        """Make sure we're decorating the patient model"""
        initial_count = Patient.objects.count()
        self.booking_patient.save()
        self.assertEquals(initial_count + 1, Patient.objects.count())
    
    def test_calculate_year_or_birth_when_setting_age(self):
        """If the patient's date of birth is unknown, automatically calculate 
        the year of birth based on the given age."""
        self.assertFalse(self.booking_patient.date_of_birth)
        self.booking_patient.age = 30
        self.booking_patient.save()
        self.assertEquals(self.booking_patient.date_of_birth.year, \
                                                    datetime.now().year - 30)
    


class AppointmentTestCase(TestCase):
    
    fixtures = ['patients', 'clinics', 'visits', 'initial_data']
    
    def setUp(self):
        self.booking_patient = create_booking_patient()
        self.booking_patient.save()
        self.appointment = Appointment()
        self.appointment.booking_patient = self.booking_patient
        self.appointment.patient = self.booking_patient.patient
        self.appointment.te_id = self.booking_patient.te_id
        self.appointment.date = datetime.now()
        self.appointment.status = 's'
        self.appointment.clinic = Clinic.objects.all()[0]
    
    def tearDown(self):
        pass
    
    def test_appointment_inheritance(self):
        initial_count = Visit.objects.count()
        self.appointment.save()
        self.assertEquals(initial_count + 1, Visit.objects.count())
    
    def test_not_calculating_risk_profile(self):
        self.appointment.save()
        # make sure we have appointments and visits which should trigger the
        # save() in Visit - which is the one we're trying to override and test
        self.assertTrue(self.booking_patient.appointment_set.count())
        self.assertTrue(self.booking_patient.visits.count())
        self.assertTrue(self.appointment.booking_patient.risk_profile == None)
    
