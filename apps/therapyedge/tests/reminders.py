from django.test import TestCase
from datetime import datetime, date, timedelta
from therapyedge import reminders_i18n
from therapyedge.models import *
from therapyedge.tests.helpers import TestingGateway, random_string
from mobile.sms.models import *

class RemindersI18NTestCase(TestCase):
    
    fixtures = ['patients', 'clinics']
    
    def setUp(self):
        self.patient = Patient.objects.all()[0]
        self.patient.save()
        self.language = self.patient.language
        self.clinic = Clinic.objects.all()[0]
        self.gateway = TestingGateway(name="testing",url="http://testingserver/")
        self.gateway.save()
    
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
        return [self.patient.visits.create(**args) for idx in \
                                            range(0, kwargs.get('amount',1))]
    
    def mark_visits(self, visits, date, status):
        return [v.events.create(date=date,status=status) for v in visits]
    
    def calculate_date(self,**kwargs):
        return datetime.now().date() + timedelta(**kwargs)
    
    def send_reminders(self, _type):
        fn = getattr(reminders_i18n, _type)
        return fn(self.gateway, Visit.objects.all(), datetime.now().date())
    
    def test_tomorrow(self):
        tomorrow = self.calculate_date(days=1)
        
        # schedule visits for given date
        self.schedule_visits_for(tomorrow)
        
        # send reminders over dummy gateway
        actions = self.send_reminders('tomorrow')
        
        # get stuff needed to test
        tomorrow_message = self.language.tomorrow_message
        tomorrow_queue = self.gateway.queue[tomorrow_message]
        
        # test!
        self.assertTrue(self.patient.active_msisdn.msisdn in tomorrow_queue)
    
    def test_twoweeks(self):
        twoweeks = self.calculate_date(days=14)
        self.schedule_visits_for(twoweeks)
        actions = self.send_reminders('two_weeks')
        twoweeks_message = self.language.twoweeks_message % {'date': twoweeks.strftime('%A %d %b')}
        twoweeks_queue = self.gateway.queue[twoweeks_message]
        self.assertTrue(self.patient.active_msisdn.msisdn in twoweeks_queue)
    
    def test_attended(self):
        yesterday = self.calculate_date(days=-1)
        visits = self.schedule_visits_for(yesterday)
        events = self.mark_visits(visits, yesterday, 'a')
        self.send_reminders('attended')
        attended_message =self.language.attended_message
        attended_queue = self.gateway.queue[attended_message]
        self.assertTrue(self.patient.active_msisdn.msisdn in attended_queue)
    
    def test_missed(self):
        yesterday = self.calculate_date(days=-1)
        visits = self.schedule_visits_for(yesterday)
        events = self.mark_visits(visits, yesterday, 'm')
        self.send_reminders('missed')
        missed_message = self.language.missed_message
        missed_queue = self.gateway.queue[missed_message]
        self.assertTrue(self.patient.active_msisdn.msisdn in missed_queue)
    
