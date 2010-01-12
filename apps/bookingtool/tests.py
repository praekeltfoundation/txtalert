"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.db.models.query import QuerySet
from django.utils import simplejson
from core.models import *
from gateway.models import SendSMS

from bookingtool.models import *
from datetime import datetime, timedelta, date
import gateway
_, gateway, sms_receipt_handler = gateway.load_backend('gateway.backends.dummy')
                            
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
        self.booking_patient.visit_set.create(date=yesterday, \
                                            te_visit_id='123',
                                            status='m', clinic=self.clinic, \
                                            visit_type='arv')
        
        tomorrow = today + timedelta(days=1)
        self.booking_patient.visit_set.create(date=tomorrow, \
                                            te_visit_id='456', 
                                            status='s', clinic=self.clinic, \
                                            visit_type='arv')
        
        self.assertTrue(isinstance(self.booking_patient.appointments, QuerySet))
        self.assertEquals(self.booking_patient.visit_set.count(), 2)
        self.assertEquals(self.booking_patient.appointments.count(), 1)
    
    def test_booking_patient_opt_in_status(self):
        patient = Patient.objects.all()[0]
        patient.created_at = datetime.now()
        patient.save()
        
        self.assertTrue(patient.opted_in)
        self.assertRaises(
            BookingPatient.DoesNotExist,
            BookingPatient.objects.get,
            patient_ptr=patient.pk
        )
        bp = BookingPatient.objects.create(
            patient_ptr=patient,
            created_at=datetime.now(),
            age=20,
            opted_in=True
        )
        # the signal should automatically match the patient and booking
        # patients opt-status
        self.assertEquals(bp.opt_status,'opt-in')
        
        # now do it the other way around
        patient.opted_in = False
        patient.save()
        bp.opt_status = 'opt-in'
        bp.opted_in = False
        bp.save()
        
        patient = Patient.objects.get(pk=patient.pk)
        self.assertEquals(patient.opted_in, True)
        bp = BookingPatient.objects.get(pk=bp.pk)
        self.assertEquals(bp.opted_in, True)
        

class CalendarTestCase(TestCase):
    
    fixtures = ['test_bookingtool_risks', 'test_therapyedge_risks']
    
    def setUp(self):
        self.client = Client()
    
    def tearDown(self):
        pass
    
    def test_risk_json_response(self):
        
        # specify booking tool risk levels for this test
        from django.conf import settings
        settings.BOOKING_TOOL_RISK_LEVELS = {
            # pc is for patient count
            'high': lambda pc: pc > 100,
            'medium': lambda pc: 50 <= pc < 100,
            'low': lambda pc: pc < 50,
        }
        
        # test the following dates for which data has been loaded in the fixtures
        risk_dates = {
            "low": date(2009, 10, 1),
            "medium": date(2009, 10, 2),
            "high": date(2009, 10, 3)
        }
        
        for risk, _date in risk_dates.items():
            get_args = {"date": _date.strftime("%Y-%m-%d")}
            response = self.client.get(reverse('calendar-risk'), get_args)
            self.assertEquals(response.status_code, 200)
            json = simplejson.loads(response.content)
            self.assertEquals(json, {"risk": risk})
    
    def test_risk_with_bad_args(self):
        response = self.client.get(reverse('calendar-risk'))
        self.assertEquals(response.status_code, 404)
    
    def test_redirect_for_today(self):
        response = self.client.get(reverse('calendar-today'))
        self.assertRedirects(response, "http://testserver%s" % reverse('calendar-date', \
                                            kwargs={
                                                'month': datetime.now().month,
                                                'year': datetime.now().year
                                        }), status_code=302)
    
    def test_calendar_rendering(self):
        patient = Patient.objects.all()[0]
        today = datetime.now()
        for a in range(0,100):
            for i in range(0,10):
                patient.visit_set.create(
                    clinic=Clinic.objects.all()[0],
                    date=datetime(today.year, today.month, 1) + timedelta(i),
                    status='s'
                )
        
        response = self.client.get(
            reverse('calendar-date', kwargs={
                'month': today.month,
                'year': today.year
            })
        )
        # 10 days should have the class 'medium' according to the current
        # BOOKING_TOOL_RISK_LEVELS in settings
        self.assertContains(response, 'medium', count=10)
    
    def test_calendar_month_rollback(self):
        response = self.client.get(
            reverse('calendar-date', kwargs={
                'month': 1,
                'year': 2010
            })
        )
        self.assertContains(response, '2009/12.html', count=1) # link to previous year
    
    def test_calendar_month_rollover(self):
        response = self.client.get(
            reverse('calendar-date', kwargs={
                'month': 12,
                'year': 2009
            })
        )
        self.assertContains(response, '2010/1.html', count=1) # link to next year
    
    def test_date_suggestion(self):
        bp = BookingPatient.objects.all()[0]
        response = self.client.get(reverse('calendar-suggest'), {
            'patient_id': bp.id
        })
        self.assertEquals(response['Content-Type'], 'text/json')
        data = simplejson.loads(response.content)
        self.assertEquals(data['suggestion'], '2009-11-2')
    
    def test_date_suggestion_for_new_unsaved_patient(self):
        response = self.client.get(reverse('calendar-suggest'), {
            'patient_id': -1,   # -1 is magic nr for no patient, this happens
                                # when we try and suggest a date for a patient
                                # that isn't saved yet
            'treatment_cycle': 1 # in months
        })
        data = simplejson.loads(response.content)
        expected_suggestion = datetime.now() + timedelta(365/12) # poor mans monthly calculation
        self.assertEquals(
            data['suggestion'], 
            '%s-%s-%s' % (
                expected_suggestion.year, 
                expected_suggestion.month,
                expected_suggestion.day
            )
        )
    
    def test_date_suggestion_for_first_visit(self):
        bp = BookingPatient.objects.all()[0]
        [v.delete() for v in bp.visit_set.all()] # clear all visits
        # make sure there are no visits, go through the regular class
        # instead of the RelatedManager because that doesn't filter out
        # soft-deleted objects
        self.assertEquals(Visit.objects.filter(patient=bp).count(), 0)
        response = self.client.get(reverse('calendar-suggest'), {
            'patient_id': bp.id
        })
        self.assertEquals(response['Content-Type'], 'text/json')
        data = simplejson.loads(response.content)
        expected_suggestion = datetime.now() + timedelta(365/12) # poor mans monthly calculation
        self.assertEquals(
            data['suggestion'], 
            '%s-%s-%s' % (
                expected_suggestion.year, 
                expected_suggestion.month,
                expected_suggestion.day
            )
        )
    
    def test_date_suggestion_without_patient_id(self):
        response = self.client.get(reverse('calendar-suggest'), {
            # no args
        })
        self.assertEquals(response.status_code, 404)
    
    def test_date_suggestion_with_treatment_cycle_override(self):
        bp = BookingPatient.objects.all()[0]
        response = self.client.get(reverse('calendar-suggest'), {
            'patient_id': bp.id,
            'treatment_cycle': 3
        })
        self.assertEquals(response['Content-Type'], 'text/json')
        data = simplejson.loads(response.content)
        self.assertEquals(data['suggestion'], '2010-1-2')
    

class VerificationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
    
    
    def test_verification_sms(self):
        msisdn = '27761234567'
        self.assertRaises(
            SendSMS.DoesNotExist,
            SendSMS.objects.get,
            msisdn=msisdn
        )
        response = self.client.post(reverse('verification-sms'), {
            'msisdn': msisdn
        })
        
        self.assertEquals(response.status_code, 200)
        self.failUnless(SendSMS.objects.get(msisdn=msisdn))
    
