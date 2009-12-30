from django.test import TestCase
from datetime import datetime, date, timedelta
from therapyedge import reminders
from therapyedge.models import *
from therapyedge.tests.utils import random_string
import hashlib
import gateway

class RemindersI18NTestCase(TestCase):
    
    fixtures = ['patients', 'clinics']
    
    def setUp(self):
        self.patient = Patient.objects.all()[0]
        self.patient.save()
        self.language = self.patient.language
        self.clinic = Clinic.objects.all()[0]
        gateway.load_backend('gateway.backends.dummy')
    
    def tearDown(self):
        pass
    
    def schedule_visits_for(self, date, **kwargs):
        args = {
            'te_visit_id': kwargs.get('te_visit_id', random_string()[:20]),
            'date': date,
            'status': kwargs.get('status', 'm'),
            'clinic': kwargs.get('clinic', self.clinic),
            'visit_type': kwargs.get('visit_type', 'arv'),
        }
        return [self.patient.visit_set.create(**args) for idx in \
                                            range(0, kwargs.get('amount',1))]
    
    def mark_visits(self, visits, date, status):
        def update_attributes(visit):
            visit.date = date
            visit.status = status
            visit.save()
            return visit
        return map(update_attributes, visits)
    
    def calculate_date(self,**kwargs):
        return datetime.now().date() + timedelta(**kwargs)
    
    def send_reminders(self, _type):
        fn = getattr(reminders, _type)
        return fn(gateway.gateway, Visit.objects.all(), datetime.now().date())
    
    def test_tomorrow(self):
        tomorrow = self.calculate_date(days=1)
        
        # schedule visits for given date
        self.schedule_visits_for(tomorrow)
        
        # send reminders over dummy gateway
        tomorrow_sms_set = self.send_reminders('tomorrow')
        
        # get stuff needed to test
        sms_set = tomorrow_sms_set[self.language]
        
        # test!
        self.assertTrue(self.patient.active_msisdn.msisdn in [sms.msisdn for sms in sms_set])
    
    def test_twoweeks(self):
        twoweeks = self.calculate_date(days=14)
        self.schedule_visits_for(twoweeks)
        twoweeks_sms_set = self.send_reminders('two_weeks')
        sms_set = twoweeks_sms_set[self.language]
        self.assertTrue(self.patient.active_msisdn.msisdn in [sms.msisdn for sms in sms_set])
    
    def test_attended(self):
        yesterday = self.calculate_date(days=-1)
        visits = self.schedule_visits_for(yesterday)
        events = self.mark_visits(visits, yesterday, 'a')
        attended_sms_set = self.send_reminders('attended')
        sms_set = attended_sms_set[self.language]
        self.assertTrue(self.patient.active_msisdn.msisdn in [sms.msisdn for sms in sms_set])
    
    def test_missed(self):
        yesterday = self.calculate_date(days=-1)
        visits = self.schedule_visits_for(yesterday)
        events = self.mark_visits(visits, yesterday, 'm')
        missed_sms_set = self.send_reminders('missed')
        sms_set = missed_sms_set[self.language]
        self.assertTrue(self.patient.active_msisdn.msisdn in [sms.msisdn for sms in sms_set])
    
