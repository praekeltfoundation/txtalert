from django.db import IntegrityError
from therapyedge.xmlrpc.client import Client
from therapyedge.models import Patient, MSISDN, Visit, Clinic

import iso8601
import re
import logging
from datetime import datetime

logger = logging.getLogger("importer")

SEX_MAP = {
    'Male': 'm',
    'Female': 'f',
    'Transgender f->m': 'f>m',
    'Transgender m->f': 'm>f'
}

# Not too sure about the quality of these, I'd prefer phone numbers
# to be normalized to one single format before entering the DB
MSISDNS_RE = re.compile(r'^([+]?(0|27)[0-9]{9}/?)+$')
MSISDN_RE = re.compile(r'[+]?(0|27)([0-9]{9})')

def get_object_or_none(model, *args, **kwargs):
    """Like get_object_or_404 but then returns None instead of raising Http404"""
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist, e:
        return None

def update_or_create_patient(te_id, **key_value_pairs):
    """not very pretty"""
    created = False
    patient = get_object_or_none(Patient, te_id=te_id)
    if not patient:
        logger.debug('Creating new Patient with te_id %s' % te_id)
        patient = Patient(te_id=te_id)
        created = True
    else:
        logger.debug('Updating patient with te_id %s' % te_id)
    for key, value in key_value_pairs.items():
        setattr(patient, key, value)
    patient.save()
    return patient, created

class VisitException(Exception): pass

class Importer(object):
        
    def __init__(self, uri=None, verbose=False):
        self.client = Client(uri, verbose)
    
    def import_all_patients(self, clinic):
        all_patients = self.client.get_all_patients(clinic.id)
        return all_patients
        # not sure what this returns since they all the RPC calls are failing
        # for me ATM
        # return self.update_local_patients(all_patients)
    
    def import_updated_patients(self, clinic, since, until=''):
        updated_patients = self.client.get_updated_patients(clinic.id, since, until)
        logger.info('Receiving updated patients for %s between %s and %s' % (
            clinic.name,
            since,
            until
        ))
        return self.update_local_patients(updated_patients)
    
    def update_local_patients(self, updated_patients):
        for remote_patient in updated_patients:
            try:
                logger.debug('Processing: %s' % remote_patient._asdict())
                local_patient, created = update_or_create_patient(
                    remote_patient.te_id,
                    age=remote_patient.age,
                    sex=(SEX_MAP.get(remote_patient.sex, None) or 't') # for some reason it defaults to transgender, no clue why
                )
                
                if created:
                    logger.debug('Patient created: %s' % local_patient)
                else:
                    logger.debug('Update for existing patient: %s' % local_patient)
                
                # `celphone` typo is TherapyEdge's
                for phone_number in remote_patient.celphone.split('/'):
                    # FIXME: normalize phone number or we'll go nuts trying
                    #        to identify patients based on their MSISDN
                    msisdn, created = MSISDN.objects.get_or_create(msisdn=phone_number)
                    if msisdn not in local_patient.msisdns.iterator():
                        local_patient.msisdns.add(msisdn)
                
                yield local_patient
            
            except IntegrityError, e:
                logger.exception('Failed to create Patient for: %s' % remote_patient)
            
        
    
    def import_coming_visits(self, clinic, since, until=''):
        coming_visits = self.client.get_coming_visits(clinic.id, since, until)
        logger.info('Receiving coming visits for %s between %s and %s' % (
            clinic.name,
            since,
            until
        ))
        return self.update_local_coming_visits(clinic, coming_visits)
    
    def update_local_coming_visits(self, clinic, visits):
        for visit in visits:
            logger.debug('Processing Visit %s' % visit._asdict())
            try:
                # I'm assuming we'll always have the patient being referenced
                # in the Visit object, if not - raise hell
                patient = Patient.objects.get(te_id=visit.te_id)
                
                local_visit = get_object_or_none(Visit, te_visit_id=visit.key_id)
                
                # If the visit doesn't exist assume it's a new one
                if not local_visit:
                    local_visit = Visit.objects.create(
                        te_visit_id=visit.key_id,
                        clinic=clinic,
                        patient=patient,
                        date=iso8601.parse_date(visit.scheduled_visit_date)
                    )
                    logger.debug('Creating new Visit: %s' % local_visit.id)
                else:
                    # if the dates differ between the existing date and the 
                    # date we're receiving from TherapyEdge then our data needs
                    # to be updated
                    scheduled_date = iso8601.parse_date(visit.scheduled_visit_date)
                    if local_visit.date != scheduled_date:
                        logger.debug('Updating existing Visit: %s' % local_visit.id)
                        # not sure why the original version of the import script
                        # only updates the date and not the status
                        local_visit.date = scheduled_date
                        local_visit.status = 's'
                        local_visit.save()
                
                yield local_visit
            except IntegrityError, e:
                logger.exception('Failed to create upcoming Visit')
            except Patient.DoesNotExist, e:
                logger.exception('Could not find Patient for Visit.te_id')
    
    def import_missed_visits(self, clinic, since, until=''):
        missed_visits = self.client.get_missed_visits(clinic.id, since, until)
        logger.info('Receiving missed visits for %s between %s and %s' % (
            clinic.name,
            since,
            until
        ))
        return self.update_local_missed_visits(clinic, missed_visits)
    
    def update_local_missed_visits(self, clinic, visits):
        for visit in visits:
            logger.debug('Processing missed Visit: %s' % visit._asdict())
            try:
                # get the patient or raise error
                patient = Patient.objects.get(te_id=visit.te_id)
                local_visit = get_object_or_none(Visit, te_visit_id=visit.key_id)
                missed_date = iso8601.parse_date(visit.missed_date).date()
                # make sure we have the visit which is going to be marked as missed
                if not local_visit:
                    local_visit = Visit.objects.create(
                        te_visit_id=visit.key_id,
                        clinic=clinic,
                        patient=patient,
                        date=missed_date,
                        status='m' # m is for missed
                    )
                    logger.debug('Creating new Visit: %s' % local_visit.id)
                else:
                    # if it is in the future it couldn't possible have been missed
                    # not sure why the original import has this
                    if missed_date > datetime.now().date():
                        raise VisitException, 'tried to mark a future visit as missed'
                
                    # if the missed date is still before the scheduled date
                    # consider it a reschedule of the date
                    if missed_date < local_visit.date:
                        status = 'r'
                    else:
                        status = 'm'
                
                    logger.debug('Updating Visit:%s, date: %s, status: %s' % (
                        local_visit.id,
                        missed_date,
                        status
                    ))
                    local_visit.date = missed_date
                    local_visit.status = status
                    local_visit.save()
                
                yield local_visit
            except IntegrityError, e:
                logger.exception('Failed to create Visit')
            except Patient.DoesNotExist, e:
                logger.exception('Could not find Patient for Visit.te_id')
            except VisitException, e:
                logger.exception('VisitException')
    
    def import_done_visits(self, clinic, since, until=''):
        done_visits = self.client.get_done_visits(clinic.id, since, until)
        logger.info('Receiving done visits for %s between %s and %s' % (
            clinic.name,
            since,
            until
        ))
        return self.update_local_done_visits(clinic, done_visits)
    
    def update_local_done_visits(self, clinic, visits):
        for visit in visits:
            logger.debug('Processing done visit: %s' % visit._asdict())
            try:
                # get patient or raise error
                patient = Patient.objects.get(te_id=visit.te_id)
                local_visit = get_object_or_none(Visit, te_visit_id=visit.key_id)
                done_date = iso8601.parse_date(visit.done_date).date()
                scheduled_date = iso8601.parse_date(visit.scheduled_date).date()
                
                # make sure we have a visit for the change we're getting
                if not local_visit:
                    local_visit = Visit.objects.create(
                        te_visit_id=visit.key_id,
                        clinic=clinic,
                        patient=patient,
                        date=scheduled_date,
                        status='s', # s for scheduled, for some reason we don't
                                    # have this visit registered, even though it
                                    # is done, do as if we already had it and
                                    # save it twice
                    )
                    
                    # save again, now with 'attended' status and the done date
                    local_visit.date = done_date
                    local_visit.status = 'a'
                    local_visit.save()
                    
                    logger.debug('Creating new done Visit: %s' % local_visit.id)
                
                else:
                    # done events we flag as a for 'attended', not sure why the orignal
                    # import script did a get_or_create here. Maybe an error or 
                    # maybe the TherapyEdge data is *really* wonky
                    logger.debug('Updating Visit: %s, date: %s, status: %s' % (
                        local_visit.id,
                        done_date,
                        'a'
                    ))
                    local_visit.date = done_date
                    local_visit.status = 'a'
                    local_visit.save()
                
                yield local_visit
            except IntegrityError, e:
                logger.exception('Failed to create visit')
            except Patient.DoesNotExist, e:
                logger.exception('Could not find Patient for Visit.te_id')
    
    def import_deleted_visits(self, since, until=''):
        deleted_visits = self.client.get_deleted_visits(since, until)
        logger.info('Receiving deleted visits between %s and %s' % (
            since,
            until
        ))
        return self.update_local_deleted_visits(deleted_visits)
    
    def update_local_deleted_visits(self, visits):
        for visit in visits:
            logger.debug('Processing deleted visit: %s' % visit._asdict())
            try:
                local_visit = Visit.objects.get(te_visit_id=visit.key_id)
                local_visit.delete()
                logger.debug('Deleted Visit: %s' % local_visit.id)
                yield local_visit
            except Visit.DoesNotExist, e:
                logger.exception('Could not find Visit to delete')
    
    def import_all_changes(self, clinic, since, until):
        # I set these because they all are generators, setting them forces
        # them to be iterated over
        set(self.import_updated_patients(clinic, since, until))
        set(self.import_coming_visits(clinic, since, until))
        set(self.import_missed_visits(clinic, since, until))
        set(self.import_done_visits(clinic, since, until))
        set(self.import_deleted_visits(since, until))
    
    