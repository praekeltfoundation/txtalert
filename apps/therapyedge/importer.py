from django.db import IntegrityError
from therapyedge.xmlrpc.client import Client
from core.models import Patient, MSISDN, Visit, Clinic

import iso8601
import re
import logging
from datetime import datetime, date

logger = logging.getLogger("importer")

PATIENT_ID_RE = re.compile(r'^[0-9]{2}-[0-9]{5}$')
PATIENT_AGE_RE = re.compile(r'^[0-9]{1,3}$')
PATIENT_SEX_RE = re.compile(r'^(Male|Female|Transgender ?(f->m|m->f)?)$')

APPOINTMENT_ID_RE = re.compile(r'^[0-9]{2}-[0-9]{9}$')
DATE_RE = re.compile(r'^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{2}:[0-9]{2}:[0-9]{2}$')

MSISDNS_RE = re.compile(r'^([+]?(0|27)[0-9]{9}/?)+$')
MSISDN_RE = re.compile(r'[+]?(0|27)([0-9]{9})')

IMPORT_CUTOFF = datetime(2009, 01, 01)
IMPORT_DAY_INTERVAL = 10

MESSAGE_PATIENTID_INCONSISTENT = "Patient ID '%s' is inconsistent with previous ID '%s' for visit '%s'."
MESSAGE_PATIENT_NOTFOUND = "Patient with the ID '%s' could not be found for visit '%s'."
MESSAGE_VISIT_NOTFOUND = "Visit with the ID '%s' could not be found."


class InvalidValueException(Exception): pass

class Validator(object):
    
    @classmethod
    def test(klass, method, error_message = 'invalid input'):
        def tester(value):
            if not method(value):
                raise InvalidValueException, error_message
            return value
        return tester
    
    @classmethod
    def regex(klass, pattern):
        """Raises an InvalidValueException if the given input does not 
        match the pattern"""
        regex = re.compile(pattern)
        return klass.test(regex.match, 'does not match pattern %s' % pattern)
    
    @classmethod
    def lookup(klass, dictionary):
        def tester(value):
            if value not in dictionary:
                raise InvalidValueException, 'not one of the available ' \
                                                'lookup keys: %s' % dictionary
            return dictionary[value]
        return tester


SEX_MAP = {
    'Male': 'm',
    'Female': 'f',
    'Transgender f->m': 'f>m',
    'Transgender m->f': 'm>f'
}

Age = Validator.regex(r'^[0-9]{1,3}$')
Sex = Validator.lookup(SEX_MAP)
TherapyEdgeId = Validator.regex(r'^\d{2}-\d{5}$')
AppointmentId = Validator.regex(r'^\d{2}-\d{9}$')
Date = Validator.regex(r'^\d{4}-\d{1,2}-\d{1,2} \d{2}:\d{2}:\d{2}$')
Msisdn = Validator.regex(r'(0|[+]?27)([0-9]{9})')

# Not too sure about the quality of these, I'd prefer phone numbers
# to be normalized to one single format before entering the DB
# MSISDNS_RE = re.compile(r'^([+]?(0|27)[0-9]{9}/?)+$')
MSISDN_RE = re.compile(r'[+]?(0|27)([0-9]{9})')

class VisitException(Exception): pass


class Update(object):
    def __init__(self, klass):
        self.klass = klass
    
    def get(self, *args, **kwargs):
        try:
            self.instance, self.created = self.klass.objects.get(*args, **kwargs), False
        except self.klass.DoesNotExist, e:
            self.instance, self.created = self.klass(*args, **kwargs), True
        return self
    
    def update_attributes(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self.instance, key, value)
        return self
    
    def save(self):
        if self.instance.is_dirty():
            self.instance.save()
        return self.instance, self.created

class Importer(object):
        
    def __init__(self, uri=None, verbose=False):
        self.client = Client(uri, verbose)
    
    def import_all_patients(self, clinic):
        # all_patients = self.client.get_all_patients(clinic.te_id)
        # return all_patients
        # not sure what this returns since they all the RPC calls are failing
        # for me ATM
        # return self.update_local_patients(all_patients)
        raise NotImplemented, 'all these are failing for me, without any '\
                                'documentation I am unable to continue'
    
    def import_updated_patients(self, clinic, since, until):
        updated_patients = self.client.get_updated_patients(clinic.te_id, since, until)
        logger.info('Receiving updated patients for %s between %s and %s' % (
            clinic.name,
            since,
            until
        ))
        return self.update_local_patients(updated_patients)
    
    def update_local_patients(self, remote_patients):
        for remote_patient in remote_patients:
            try:
                yield self.update_local_patient(remote_patient)
            except IntegrityError, e:
                logger.exception('Failed to create Patient for: %s' % remote_patient)
    
    def update_local_patient(self, remote_patient):
        logger.debug('Processing: %s' % remote_patient._asdict())
        
        patient, created = Update(Patient) \
                                .get(te_id=remote_patient.te_id) \
                                .update_attributes(
                                    age = Age(remote_patient.age),
                                    sex = Sex(remote_patient.sex)
                                ).save()
        if created:
            logger.debug('Patient created: %s' % patient)
        else:
            logger.debug('Update for existing patient: %s' % patient)
        
        # `celphone` typo is TherapyEdge's
        for msisdn in remote_patient.celphone.split('/'):
            # FIXME: this normalization seems sketchy at best
            match = MSISDN_RE.match(msisdn)
            if match:
                phone_number = '27' + match.groups()[1]
                msisdn, created = MSISDN.objects.get_or_create(msisdn=phone_number)
                if msisdn not in patient.msisdns.all():
                    patient.msisdns.add(msisdn)
        
        return patient
            
        
    
    def import_coming_visits(self, clinic, since, until):
        coming_visits = self.client.get_coming_visits(clinic.te_id, since, until)
        logger.info('Receiving coming visits for %s between %s and %s' % (
            clinic.name,
            since,
            until
        ))
        return self.update_local_coming_visits(clinic, coming_visits)
    
    def update_local_coming_visits(self, clinic, visits):
        for visit in visits:
            logger.debug('Processing coming Visit %s' % visit._asdict())
            try:
                yield self.update_local_coming_visit(clinic, visit)
            except IntegrityError, e:
                logger.exception('Failed to create upcoming Visit')
            except Patient.DoesNotExist, e:
                logger.exception('Could not find Patient for Visit.te_id')
    
    def update_local_coming_visit(self, clinic, remote_visit):
        # I'm assuming we'll always have the patient being referenced
        # in the Visit object, if not - raise hell
        patient = Patient.objects.get(te_id=remote_visit.te_id)
        coming_date = iso8601.parse_date(remote_visit.scheduled_visit_date)
        
        try:
            visit = Visit.objects.get(te_visit_id=remote_visit.key_id)
            created = False
        except Visit.DoesNotExist:
            visit = Visit(te_visit_id=remote_visit.key_id)
            created = True
        
        # check if something actually changed in the visit, if not, immediately
        # return the visit - no use continuing
        if coming_date.date() == visit.date:
            return visit
        
        # it's a new visit
        if created:
            if coming_date.date() <= date.today():
                visit.status = 'm'
            else:
                visit.status = 's'
        # it's an existing visit
        else:
            if coming_date.date() > visit.date:
                visit.status = 'r'
            else:
                visit.status = 'm'
        
        visit.clinic = clinic
        visit.patient = patient
        visit.date = coming_date
        if visit.is_dirty():
            visit.save()
        
        if created:
            logger.debug('Creating new Visit: %s' % visit.id)
        else:
            logger.debug('Updating existing Visit: %s / (%s vs %s)' % (visit.id, visit.get_dirty_fields(), visit._original_state))
        return visit
    
    def import_missed_visits(self, clinic, since, until):
        missed_visits = self.client.get_missed_visits(clinic.te_id, since, until)
        logger.info('Receiving missed visits for %s between %s and %s' % (
            clinic.name,
            since,
            until
        ))
        return self.update_local_missed_visits(clinic, missed_visits)
    
    def update_local_missed_visits(self, clinic, missed_visits):
        for visit in missed_visits:
            logger.debug('Processing missed Visit: %s' % visit._asdict())
            try:
                yield self.update_local_missed_visit(clinic, visit)
            except IntegrityError, e:
                logger.exception('Failed to create Visit')
            except Patient.DoesNotExist, e:
                logger.exception('Could not find Patient for Visit.te_id')
            except VisitException, e:
                logger.exception('VisitException')
    
    def update_local_missed_visit(self, clinic, remote_visit):
        # get the patient or raise error
        patient = Patient.objects.get(te_id=remote_visit.te_id)
        missed_date = iso8601.parse_date(remote_visit.missed_date).date()
        
        try:
            visit = Visit.objects.get(te_visit_id=remote_visit.key_id)
            created = False
        except Visit.DoesNotExist:
            visit = Visit(te_visit_id=remote_visit.key_id)
            created = True
        
        # check if something actually changed in the visit, if not, immediately
        # return the visit - no use continuing
        if missed_date == visit.date:
            return visit
        
        # it's a new visit
        if created:
            if missed_date <= date.today():
                visit.status = 'm'
            else:
                visit.status = 'r'
        # it's an existing visit
        else:
            if missed_date > visit.date:
                visit.status = 'r'
            else:
                visit.status = 'm'
        
        visit.clinic = clinic
        visit.patient = patient
        visit.date = missed_date
        if visit.is_dirty():
            visit.save()
        
        if created:
            logger.debug('Creating new Visit: %s' % visit.id)
        else:
            logger.debug('Updating Visit:%s, date: %s, status: %s' % (
                visit.id,
                missed_date,
                visit.status
            ))
        
        return visit
    
    def import_done_visits(self, clinic, since, until):
        done_visits = self.client.get_done_visits(clinic.te_id, since, until)
        logger.info('Receiving done visits for %s between %s and %s' % (
            clinic.name,
            since,
            until
        ))
        return self.update_local_done_visits(clinic, done_visits)
    
    def update_local_done_visits(self, clinic, remote_visits):
        for remote_visit in remote_visits:
            logger.debug('Processing done Visit: %s' % remote_visit._asdict())
            try:
                yield self.update_local_done_visit(clinic, remote_visit)
            except IntegrityError, e:
                logger.exception('Failed to create visit')
            except Patient.DoesNotExist, e:
                logger.exception('Could not find Patient for Visit.te_id')
        
    
    def update_local_done_visit(self, clinic, remote_visit):
        # get patient or raise error
        patient = Patient.objects.get(te_id=remote_visit.te_id)
        done_date = iso8601.parse_date(remote_visit.done_date).date()
        
        visit, created = Update(Visit) \
                            .get(te_visit_id=remote_visit.key_id) \
                            .update_attributes(
                                clinic=clinic,
                                patient=patient,
                                date=done_date,
                                status='a'
                            ).save()
        
        # make sure we have a visit for the change we're getting
        if created:
            logger.debug('Creating new done Visit: %s' % visit.id)
        else:
            # done events we flag as a for 'attended', not sure why the orignal
            # import script did a get_or_create here. Maybe an error or 
            # maybe the TherapyEdge data is *really* wonky
            logger.debug('Updating Visit: %s, date: %s, status: %s' % (
                visit.id,
                done_date,
                'a'
            ))
        return visit
    
    def import_deleted_visits(self, clinic, since, until):
        deleted_visits = self.client.get_deleted_visits(clinic.te_id, since, until)
        logger.info('Receiving deleted visits between %s and %s' % (
            since,
            until
        ))
        return self.update_local_deleted_visits(deleted_visits)
    
    def update_local_deleted_visits(self, remote_visits):
        for remote_visit in remote_visits:
            logger.debug('Processing deleted Visit: %s' % remote_visit._asdict())
            try:
                yield self.update_local_deleted_visit(remote_visit)
            except Visit.DoesNotExist, e:
                logger.exception('Could not find Visit to delete')
    
    def update_local_deleted_visit(self, remote_visit):
        visit = Visit.objects.get(te_visit_id=remote_visit.key_id)
        visit.delete()
        logger.debug('Deleted Visit: %s' % visit.id)
        return visit
    
    def import_all_changes(self, clinic, since, until):
        # I set these because they all are generators, listing them forces
        # them to be iterated over
        return {
            # 'all_patients': list(self.import_all_patients(clinic)),
            'updated_patients': list(self.import_updated_patients(clinic, since, until)),
            'coming_visits': list(self.import_coming_visits(clinic, since, until)),
            'missed_visits': list(self.import_missed_visits(clinic, since, until)),
            'done_visits': list(self.import_done_visits(clinic, since, until)),
            'deleted_visits': list(self.import_deleted_visits(clinic, since, until))
        }
    
    
