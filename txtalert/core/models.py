#  This file is part of TxtAlert.
#
#  TxtALert is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TxtAlert is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with TxtAlert.  If not, see <http://www.gnu.org/licenses/>.


from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from dirtyfields import DirtyFieldsMixin
from history.models import HistoricalRecords
from datetime import datetime, date, timedelta
import logging

VISIT_STATUS_CHOICES = (
    ('m', 'Missed'),
    ('r', 'Rescheduled'),
    ('s', 'Scheduled'),
    ('a', 'Attended'),
)


class MSISDN(models.Model):
    msisdn = models.CharField('MSISDN', max_length=32, unique=True)

    class Meta:
        verbose_name = 'Mobile Number'
        verbose_name_plural = 'Mobile Numbers'
        ordering=['-id']
    
    def __unicode__(self):
        return self.msisdn


class Language(models.Model):
    name = models.CharField('Name', max_length=50)
    missed_message = models.TextField('Missed Message')
    attended_message = models.TextField('Attended Message')
    tomorrow_message = models.TextField('Tomorrow Message')
    twoweeks_message = models.TextField('Two Weeks Message')
    
    def __unicode__(self):
        return self.name
    


class Clinic(models.Model):
    te_id = models.CharField('TE ID', max_length=2, unique=True)
    active = models.BooleanField(default=True)
    name = models.CharField('Name', max_length=100)
    user = models.ForeignKey(User, related_name='clinic', blank=True, 
                                null=True)
    
    class Meta:
        verbose_name = 'Clinic'
        verbose_name_plural = 'Clinics'
    
    def __unicode__(self):
        return self.name
    


class FilteredQuerySetManager(models.Manager):
    def __init__(self, *args, **kwargs):
        super(FilteredQuerySetManager, self).__init__()
        self.args = args
        self.kwargs = kwargs
    
    def get_query_set(self):
        return super(FilteredQuerySetManager, self) \
                .get_query_set() \
                .filter(*self.args, **self.kwargs)

class SoftDeleteMixin(object):
    
    def really_delete(self, *args, **kwargs):
        super(SoftDeleteMixin, self).delete(*args, **kwargs)
    
    def delete(self):
        """
        Implementing soft delete, this isn't possible with signals as far
        as I know since there isn't a way to cancel the delete to be executed
        """
        if not self.deleted:
            self.deleted = True
            self.save()
    


class AuthProfile(models.Model):
    user = models.OneToOneField('auth.User')
    patient = models.OneToOneField('Patient')
    
    def __unicode__(self):
        return u"AuthProfile for %s - %s" % (self.patient, self.user)

class Patient(DirtyFieldsMixin, SoftDeleteMixin, models.Model):
    SEX_CHOICES = (
        ('m', 'male'),
        ('f', 'female'),
        ('t', 'transgender'),
        ('f>m', 'transgender f>m'),
        ('m>f', 'transgender m>f'),
    )
    
    REGIMENT_CHOICES = (
        (28, 'Monthly'),
        (28*2, 'Bi-monthly'),
        (28*3, 'Tri-monthly'),
    )
    
    owner = models.ForeignKey('auth.User')
    te_id = models.CharField('MRS ID', max_length=255, unique=True)
    name = models.CharField(blank=True, max_length=100)
    surname = models.CharField(blank=True, max_length=100)
    msisdns = models.ManyToManyField(MSISDN, related_name='contacts')
    active_msisdn = models.ForeignKey(MSISDN, verbose_name='Active MSISDN', 
                                        null=True, blank=True)
    
    age = models.IntegerField('Age')
    regiment = models.IntegerField(blank=True, null=True, choices=REGIMENT_CHOICES)
    sex = models.CharField('Gender', max_length=3, choices=SEX_CHOICES)
    opted_in = models.BooleanField('Opted In', default=True)
    disclosed = models.BooleanField('Disclosed', default=False)
    deceased = models.BooleanField('Deceased', default=False)
    last_clinic = models.ForeignKey(Clinic, verbose_name='Clinic', 
                                        blank=True, null=True)
    risk_profile = models.FloatField('Risk Profile', blank=True, null=True)
    language = models.ForeignKey(Language, verbose_name='Language', default=1)
    
    # soft delete
    deleted = models.BooleanField(default=False)
    
    # modification audit trail methods
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # custom manager that excludes all deleted patients
    objects = FilteredQuerySetManager(deleted=False)
    
    # normal custom manager, including deleted patients
    all_objects = models.Manager()
    
    # history of all patients
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
    
    def __unicode__(self):
        return self.te_id
    
    def clinics(self):
        return set([visit.clinic for visit in \
                        Visit.objects.filter(patient=self).order_by('-date')])
    
    def get_last_clinic(self):
        visit_qs = Visit.objects.filter(patient=self)
        if visit_qs.exists(): 
            return visit_qs.latest('id').clinic
        return None
    
    def next_visit(self):
        if self.visit_set.upcoming().exists():
            return self.visit_set.filter(status__in=['s','r'], date__gte=date.today())\
                .order_by('date')[0]
    
    def last_visit(self):
        try:
            return self.visit_set.past().filter(status='a')[0]
        except IndexError:
            return None
    
    def get_display_name(self):
        if self.surname and self.name:
            return u'%s, %s' % (self.surname, self.name)
        else:
            return u'Anonymous'
    
    def regiment_remaining(self):
        last_visit = self.last_visit()
        if last_visit:
            next_visit = last_visit.date + timedelta(days=self.regiment)
            delta = next_visit - date.today()
            return delta
        else:
            return None
    
    def next_visit_dates(self, visit = None, span=7):
        last_visit = visit or self.last_visit()
        if last_visit:
            last_visit_date = last_visit.date
        else:
            last_visit_date = date.today()
        if self.regiment:
            next_visit = last_visit_date + timedelta(days=self.regiment)
            return [next_visit + timedelta(days=i) for i in range(-span, span)]
        else:
            return [last_visit_date + timedelta(days=i) for i in range(-span,span)]
        

class VisitManager(FilteredQuerySetManager):
    def upcoming(self):
        return self.get_query_set().filter(date__gte=date.today())
    
    def past(self):
        return self.get_query_set().filter(date__lt=date.today())

class Visit(DirtyFieldsMixin, SoftDeleteMixin, models.Model):
    
    VISIT_TYPES = (
        ('arv', 'ARV'),
        ('medical', 'Medical'), 
        ('counselor', 'Counselor'),
        ('pediatric', 'Pediatric'),
        ('unknown', 'Unknown'),
    )
    
    patient = models.ForeignKey(Patient)
    te_visit_id = models.CharField('TE Visit id', max_length=20, unique=True,
                                    null=True)
    date = models.DateField('Date')
    status = models.CharField('Status', max_length=1, 
                                choices=VISIT_STATUS_CHOICES)
    comment = models.TextField('Reason', default='')
    clinic = models.ForeignKey(Clinic)
    visit_type = models.CharField('Visit Type', blank=True, max_length=80, 
                                    choices=VISIT_TYPES)
    
    # soft delete
    deleted = models.BooleanField(default=False)
    
    # modification audit trail methods
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # custom manager that excludes all deleted patients
    objects = VisitManager(deleted=False)
    
    # normal custom manager, including deleted patients
    all_objects = models.Manager()
    
    # keep track of Visit changes over time
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = 'Visit'
        verbose_name_plural = 'Visits'
        ordering = ['date']
        get_latest_by = 'id'
    
    def reschedule_earlier(self):
        return self.changerequest_set.create(request='Patient has requested '
            'the appointment to be rescheduled to an earlier date.', 
            request_type='earlier_date', status='pending')
    
    def reschedule_later(self):
        return self.changerequest_set.create(request='Patient has requested '
            'the appointment to be rescheduled to a later date.', 
            request_type='later_date', status='pending')
    
    def __unicode__(self):
        return "%s at %s" % (self.get_visit_type_display(), self.date)
    


class PleaseCallMe(models.Model):
    REASON_CHOICES = (
        ('ne', 'Khumbu did not phone back the patient'),
        ('er', 'Patient did not try to reach us'),
        ('lt', 'LTFU'),
        ('de', 'Defaulter'),
        ('na', 'No Answer'),
        ('rm', 'Reschedule missed appointment'),
        ('rf', 'Reschedule future appointment'),
        ('ca', 'Confirm appointment'),
        ('vm', 'Voicemail'),
        ('ot', 'Other (fill in notes)'),
    )
    
    user = models.ForeignKey(User)
    msisdn = models.ForeignKey(MSISDN, related_name='pcms', verbose_name='Mobile Number')
    timestamp = models.DateTimeField('Date & Time', auto_now_add=False)
    reason = models.CharField('Reason', max_length=2, choices=REASON_CHOICES, default='nc')
    notes = models.TextField('Notes', blank=True)
    message = models.TextField('Received SMS Message', blank=True)
    clinic = models.ForeignKey(Clinic, related_name='pcms', blank=True, null=True)

    class Meta:
        verbose_name = 'Please Call Me'
        verbose_name_plural = 'Please Call Me(s)'

    def __unicode__(self):
        return '%s - %s' % (self.msisdn, self.timestamp)
    
class Event(models.Model):
    """A description of an event; taxi strike, power failure etc..."""
    description = models.TextField("What happened?", blank=False)
    created_at = models.DateTimeField(blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, auto_now=True)

    def __unicode__(self):
        return u"%s... on %s" % (self.description[:50], self.created_at)

class ChangeRequest(models.Model):
    visit = models.ForeignKey(Visit)
    request = models.TextField(blank=False)
    created_at = models.DateTimeField(blank=False, auto_now_add=True)
    updated_at = models.DateTimeField(blank=False, auto_now=True)
    request_type = models.CharField(blank=False, max_length=100, choices=(
        ('earlier_date', 'Earlier date'),
        ('later_date', 'Later date'),
    ))
    status = models.CharField(blank=False, max_length=100, choices=(
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ), default='pending')
    
    class Meta:
        ordering = ['-created_at']
    
    def __unicode__(self):
        return u"ChangeRequest for %s" % self.visit


# signals
from txtalert.core import signals
from txtalert.apps.gateway.models import PleaseCallMe as GatewayPleaseCallMe

pre_save.connect(signals.check_for_opt_in_changes_handler, sender=Patient)
pre_save.connect(signals.find_clinic_for_please_call_me_handler, sender=PleaseCallMe)
pre_save.connect(signals.update_active_msisdn_handler, sender=Patient)
post_save.connect(signals.track_please_call_me_handler, sender=GatewayPleaseCallMe)
post_save.connect(signals.calculate_risk_profile_handler, sender=Visit)
