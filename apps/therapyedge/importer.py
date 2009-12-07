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

class VisitException(Exception): pass

class Importer(object):
        
    def __init__(self, uri=None, verbose=False):
        self.client = Client(uri, verbose)
    
    def import_all_patients(self, clinic_id):
        all_patients = self.client.get_all_patients(clinic_id)
        # not sure what this returns since they all the RPC calls are failing
        # for me ATM
        # return self.update_local_patients(all_patients)
    
    def import_updated_patients(self, clinic, since, until=None):
        updated_patients = self.client.get_updated_patients(clinic.id, since, until)
        return self.update_local_patients(updated_patients)
    
    def update_local_patients(self, updated_patients):
        for remote_patient in updated_patients:
            try:
                local_patient, created = Patient.objects.get_or_create(
                    te_id=remote_patient.te_id,
                    age=remote_patient.age,
                    sex=SEX_MAP.get(remote_patient.sex, None) or 't'
                )
                
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
            
        
    
    def import_coming_visits(self, clinic, since, until=None):
        coming_visits = self.client.get_coming_visits(clinic.id, since, until)
        return self.update_local_coming_visits(clinic, coming_visits)
    
    def update_local_coming_visits(self, clinic, visits):
        for visit in visits:
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
                else:
                    # if the dates differ between the existing date and the 
                    # date we're receiving from TherapyEdge then our data needs
                    # to be updated
                    scheduled_date = iso8601.parse_date(visit.scheduled_visit_date)
                    if local_visit.date != scheduled_date:
                        # not sure why the original version of the import script
                        # only updates the date and not the status
                        local_visit.date = scheduled_date
                        local_visit.events.create(date=scheduled_date, status='s')
                        local_visit.save()
                
                yield local_visit
            except IntegrityError, e:
                logger.exception('Failed to create upcoming Visit')
            except Patient.DoesNotExist, e:
                logger.exception('Could not find Patient for Visit.te_id')
    
    def import_missed_visits(self, clinic, since, until=None):
        missed_visits = self.client.get_missed_visits(clinic.id, since, until)
        return self.update_local_missed_visits(clinic, missed_visits)
    
    def update_local_missed_visits(self, clinic, visits):
        for visit in visits:
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
                        date=missed_date
                    )
                
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
                local_visit.events.create(date=missed_date, status=status)
                
                yield local_visit
            except IntegrityError, e:
                logger.exception('Failed to create Visit')
            except Patient.DoesNotExist, e:
                logger.exception('Could not find Patient for Visit.te_id')
            except VisitException, e:
                logger.exception('VisitException')
    
    def import_done_visits(self, clinic, since, until=None):
        done_visits = self.client.get_done_visits(clinic.id, since, until)
        return self.update_local_done_visits(clinic, done_visits)
    
    def update_local_done_visits(self, clinic, visits):
        for visit in visits:
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
                        date=scheduled_date
                    )
                # done events we flag as a for 'attended', not sure why the orignal
                # import script did a get_or_create here. Maybe an error or 
                # maybe the TherapyEdge data is *really* wonky
                local_visit.events.get_or_create(date=done_date, status='a')
                
                yield local_visit
            except IntegrityError, e:
                logger.exception('Failed to create visit')
            except Patient.DoesNotExist, e:
                logger.exception('Could not find Patient for Visit.te_id')
    
    def import_deleted_visits(self, since, until=None):
        deleted_visits = self.client.get_deleted_visits(since, until)
        return self.update_local_deleted_visits(deleted_visits)
    
    def update_local_deleted_visits(self, visits):
        for visit in visits:
            try:
                local_visit = Visit.objects.get(te_visit_id=visit.key_id)
                local_visit.delete()
                yield local_visit
            except Visit.DoesNotExist, e:
                logger.exception('Could not find Visit to delete')
