from django.test import TestCase
from django.contrib.auth.models import User, Group
from datetime import datetime, date, timedelta
from txtalert.apps.therapyedge import reminders
from txtalert.core.models import *
from txtalert.core.utils import random_string
from txtalert.apps.gateway.models import SendSMS
import hashlib
from txtalert.apps import gateway

class RemindersI18NTestCase(TestCase):
    
    fixtures = ['patients', 'clinics']
    
    def setUp(self):
        self.patient = Patient.objects.all()[0]
        self.patient.save()
        self.language = self.patient.language
        self.clinic = Clinic.objects.all()[0]
        self.group = Group.objects.get(name='Temba Lethu')
        self.user = User.objects.get(username='kumbu')
        self.user.groups.add(self.group)
        gateway.load_backend('txtalert.apps.gateway.backends.dummy')
    
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
        return fn(gateway.gateway, self.user, Visit.objects.all(), datetime.now().date())
    
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
    
    def test_send_stats(self):
        today = datetime.now()
        one_day = timedelta(days=1)
        one_week = timedelta(weeks=1)
        yesterday = today - one_day
        tomorrow = today + one_day
        two_weeks = today + (one_week * 2)
        
        # These settings are needed by the reminder script
        from txtalert.apps.general.settings.models import Setting
        Setting.objects.create(
            name='Stats Emails',
            type='t',
            text_value='simon@soocial.com'
        )
        
        Setting.objects.create(
            name='Stats MSISDNs',
            type='t',
            text_value='27123456789'
        )
        
        def create_visit(status, date):
            """helper function for creating visits easily"""
            return Visit.objects.create(
                patient=self.patient, 
                status=status,
                clinic=self.clinic,
                date=date
            )
        
        # setup visits to test
        visit_yesterday_attended = create_visit('a', yesterday)
        visit_yesterday_missed = create_visit('m', yesterday)
        visit_tomorrow_scheduled = create_visit('s', tomorrow)
        visit_tomorrow_rescheduled = create_visit('r', tomorrow)
        visit_two_weeks_scheduled = create_visit('s', two_weeks)
        visit_two_weeks_rescheduled = create_visit('r', two_weeks)
        
        # send the SMSs over the dummy gateway
        # FIXME: rename `all` method to something more explicit
        group_names = [group.name for group in Group.objects.all()]
        reminders.all(gateway.gateway, group_names)
        # send the stats
        reminders.send_stats(gateway.gateway, group_names, today.date())
        
        # test the emails being sent out
        from django.core import mail
        self.assertEquals(len(mail.outbox), 1)
        # our stats message is the only one in the outbox
        message = mail.outbox[0]
        # we're expecting it to have the following body, based on the visits
        # created earlier
        expecting_mail_body = reminders.REMINDERS_EMAIL_TEXT % {
            'total': 4, # because the scheduleds & rescheduleds are on the same they
                        # we'll only be sending them 1 sms instead of 2, resulting in
                        # a total of 4 instead of 6 messages being sent.
            'date': today.date(),
            'attended': 1,
            'missed': 1,
            'missed_percentage': (1.0/2.0 * 100), # 1 out of 2 visits was missed
            'tomorrow': 2,
            'two_weeks': 2
        }
        # check if this is so
        self.assertEquals(message.body, expecting_mail_body)
        self.assertTrue('simon@soocial.com' in message.to)
        
        # the latest SMS sent should be the stats SMS
        stat_sms = SendSMS.objects.latest()
        expecting_sms_text = reminders.REMINDERS_SMS_TEXT % {
            'total': 4, 
            'attended': 1,
            'missed': 1, 
            'missed_percentage': (1.0/2.0 * 100),
            'tomorrow': 2, 
            'two_weeks': 2,
        }
        self.assertEquals(stat_sms.smstext, expecting_sms_text)
        self.assertEquals(stat_sms.msisdn, '27123456789')
        
