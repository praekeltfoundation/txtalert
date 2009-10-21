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
from therapyedge.models import *
from therapyedge.tests.helpers import TestingGateway
from bookingtool.models import *
from mobile.sms.models import OperaGateway
from datetime import datetime, timedelta, date


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
        self.booking_patient.visits.create(date=yesterday, \
                                            te_visit_id='123',
                                            status='m', clinic=self.clinic, \
                                            visit_type='arv')
        
        tomorrow = today + timedelta(days=1)
        self.booking_patient.visits.create(date=tomorrow, \
                                            te_visit_id='456', 
                                            status='s', clinic=self.clinic, \
                                            visit_type='arv')
        
        self.assertTrue(isinstance(self.booking_patient.appointments, QuerySet))
        self.assertEquals(self.booking_patient.visits.count(), 2)
        self.assertEquals(self.booking_patient.appointments.count(), 1)


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
    
    def test_redirect_for_today(self):
        response = self.client.get(reverse('calendar-today'))
        self.assertRedirects(response, "http://testserver%s" % reverse('calendar-date', \
                                            kwargs={
                                                'month': datetime.now().month,
                                                'year': datetime.now().year
                                        }), status_code=302)


class VerificationTestCase(TestCase):
    def setUp(self):
        
        # monkey patching alert
        def monkey_patched_sendSMS(_self, msisdns, message):
            _self.queue[message] = msisdns
            return _self.logAction(datetime.now(), datetime.now(), \
                                            [(m, 'u') for m in msisdns], message)
            
        def monkey_patched_queue(_self):
            if not hasattr(_self, '_queue'):
                _self._queue = {}
            return _self._queue
        
        
        OperaGateway.queue = property(monkey_patched_queue)
        OperaGateway.sendSMS = monkey_patched_sendSMS
        
        self.gateway = OperaGateway(method='send', service='123', password='bla', \
                                        channel='123', name='test', \
                                        url='http://testserver.com')
        self.gateway.save()
        self.client = Client()
    
    
    def test_verification_sms(self):
        msisdn = '27761234567'
        response = self.client.post(reverse('verification-sms'), {
            'msisdn': msisdn
        })
        self.assertEquals(response.status_code, 200)
        # ugh sorry, hairy database schema
        gateway = OperaGateway.objects.all()[0]
        action = gateway.smssendactions.all()[0]
        smslog = action.smslogs.all()[0]
        self.assertTrue(smslog.contact.msisdn == msisdn)