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
from django.contrib.auth.models import Group


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

    def __unicode__(self):
        return self.msisdn


class Contact(models.Model):
    buddies = models.ManyToManyField('Contact', symmetrical=False, through='Relation')
    msisdns = models.ManyToManyField(MSISDN, related_name='contacts')
    active_msisdn = models.ForeignKey(MSISDN, verbose_name='Active MSISDN', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
    
    def __unicode__(self):
        return ('%s - ' % self.id) + u'/'.join([str(msisdn) for msisdn in self.msisdns.all()])
    
    def save(self, *args, **kwargs):
        super(Contact, self).save(*args, **kwargs)
        msisdns = self.msisdns.all()
        if not self.active_msisdn and len(msisdns) > 0:
            self.active_msisdn = msisdns[0]


class Relation(models.Model):
    contact = models.ForeignKey(Contact, related_name='relations')
    relation = models.ForeignKey(Contact, related_name='contacts')
    description = models.TextField('Description')


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
    name = models.CharField('Name', max_length=100)
    group = models.ForeignKey(Group, related_name='clinic', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Clinic'
        verbose_name_plural = 'Clinics'
    
    def __unicode__(self):
        return self.name
    


class Patient(Contact):
    SEX_CHOICES = (
        ('m', 'male'),
        ('f', 'female'),
        ('t', 'transgender'),
        ('f>m', 'transgender f>m'),
        ('m>f', 'transgender m>f'),
    )

    te_id = models.CharField('TE ID', max_length=10, unique=True)
    age = models.IntegerField('Age')
    sex = models.CharField('Sex', max_length=3, choices=SEX_CHOICES)
    opted_in = models.BooleanField('Opted In', default=False)
    disclosed = models.BooleanField('Disclosed', default=False)
    deceased = models.BooleanField('Deceased', default=False)
    last_clinic = models.ForeignKey(Clinic, verbose_name='Last Clinic', blank=True, null=True)
    risk_profile = models.FloatField('Risk Profile', blank=True, null=True)
    language = models.ForeignKey(Language, verbose_name='Language', default=1)

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def __unicode__(self):
        return self.te_id

    def get_last_clinic(self):
        if self.visits.count():
            return self.visits.latest('date').clinic
        else:
            return None

class Visit(models.Model):
    
    VISIT_TYPES = (
        ('arv', 'ARV'),
        ('medical', 'Medical'), 
        ('counselor', 'Counselor'),
        ('pediatric', 'Pediatric'),
    )
    
    patient = models.ForeignKey(Patient, related_name='visits')
    te_id = models.CharField('TE ID', max_length=20, unique=True)
    date = models.DateField('Date')
    status = models.CharField('Status', max_length=1, choices=VISIT_STATUS_CHOICES)
    clinic = models.ForeignKey(Clinic, verbose_name='Clinic', related_name='visits')
    visit_type = models.CharField('Visit Type', blank=True, max_length=80, choices=VISIT_TYPES)

    class Meta:
        verbose_name = 'Visit'
        verbose_name_plural = 'Visits'
        ordering = ['date']

    def __unicode__(self):
        return self.te_id

    def save(self, *args, **kwargs):
        patient = self.patient
        if patient.visits.count() == 0:
            patient.last_clinic = self.clinic
        else:
            patient.last_clinic = patient.get_last_clinic()
            patient.risk_profile = float(patient.visits.filter(status='m').count()) / patient.visits.count()
        patient.save()
        super(Visit, self).save(*args, **kwargs)


class VisitEvent(models.Model):
    visit = models.ForeignKey(Visit, related_name='events')
    date = models.DateField('Date')
    status = models.CharField('Status', max_length=1, choices=VISIT_STATUS_CHOICES, default='s')
    reason = models.TextField('Reason', default='')

    class Meta:
        verbose_name = 'Visit Event'
        verbose_name_plural = 'Visit Events'
        ordering = ['date']

    def __unicode__(self):
        return '%s (%s)' % (self.visit, self.status)

    def save(self, *args, **kwargs):
        super(VisitEvent, self).save(*args, **kwargs)
        if self.date == self.visit.events.order_by('-date')[:1][0].date:
            self.visit.status = self.status
            self.visit.save()


class ImportEvent(models.Model):
    content_type = models.ForeignKey(ContentType)
    clinic = models.ForeignKey(Clinic, related_name='importevents')
    stamp = models.DateTimeField('Date & Time', auto_now_add=True)
    new = models.IntegerField('New Records')
    updated = models.IntegerField('Updated Records')
    errors = models.IntegerField('Errors')

    def __init__(self, *args, **kwargs):
        if 'events' in kwargs.keys():
            events = kwargs['events']
            del kwargs['events']
            kwargs.update({'new':events.new, 'updated':events.updated, 'errors':events.errors})
        super(ImportEvent, self).__init__(*args, **kwargs)

    class Meta:
        verbose_name = 'Import Event'
        verbose_name_plural = 'Import Events'

    def __unicode__(self):
        return '%s - New: %s, Updated: %s, Errors: %s' % (self.stamp, self.new, self.updated, self.errors)


class PleaseCallMe(models.Model):
    REASON_CHOICES = (
        ('nc', 'Not Called'),
        ('na', 'No Answer'),
        ('rm', 'Reschedule missed appointment'),
        ('rf', 'Reschedule future appointment'),
        ('ca', 'Confirm appointment'),
        ('ot', 'Other (fill in notes)'),
    )

    msisdn = models.ForeignKey(MSISDN, related_name='pcms', verbose_name='Mobile Number')
    timestamp = models.DateTimeField('Date & Time', auto_now_add=False)
    reason = models.CharField('Reason', max_length=2, choices=REASON_CHOICES, default='nc')
    notes = models.TextField('Notes', blank=True)
    clinic = models.ForeignKey(Clinic, related_name='pcms', blank=True, null=True)

    class Meta:
        verbose_name = 'Please Call Me'
        verbose_name_plural = 'Please Call Me(s)'

    def __unicode__(self):
        return '%s - %s' % (self.msisdn, self.timestamp)

    def save(self, *args, **kwargs):
        # todo: currently we select the first patient we have attached to the msisdn
        if not self.clinic:
            patient = Patient.objects.get(id=self.msisdn.contacts.all()[0].id)
            self.clinic = patient.get_last_clinic()
        super(PleaseCallMe, self).save(*args, **kwargs)
