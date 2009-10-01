"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.db.models.query import QuerySet
from therapyedge.models import *
from bookingtool.models import *
from datetime import datetime, timedelta


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
        self.clinic = Clinic.objects.all()[0]
    
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
    
    def test_booking_patient_appointments(self):
        # make sure it's saved
        self.booking_patient.save()
        
        # create one event in the past and one in the future
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        self.booking_patient.visits.create(te_id="123", date=yesterday,\
                                            status='m', clinic=self.clinic, \
                                            visit_type='arv')
        
        tomorrow = today + timedelta(days=1)
        self.booking_patient.visits.create(te_id="456", date=tomorrow,\
                                            status='s', clinic=self.clinic, \
                                            visit_type='arv')
        
        self.assertTrue(isinstance(self.booking_patient.appointments, QuerySet))
        self.assertEquals(self.booking_patient.visits.count(), 2)
        self.assertEquals(self.booking_patient.appointments.count(), 1)
