from django.db import IntegrityError
from therapyedge.xmlrpc.client import Client
from therapyedge.models import Patient, MSISDN, Visit, Clinic

import iso8601
import re
import logging

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

class Importer(object):
    
    fixtures = ['patients','clinics','visits']
    
    def __init__(self, uri=None, verbose=False):
        self.client = Client(uri, verbose)
    
    def import_all_patients(self, clinic_id):
        all_patients = self.client.get_all_patients(clinic_id)
        # not sure what this returns since they all the RPC calls are failing
        # for me ATM
        # return self.update_local_patients(all_patients)
    
    def import_updated_patients(self, clinic_id, since, until=None):
        updated_patients = self.client.get_updated_patients(clinic_id, since, until)
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
            
        
    
    def import_coming_visits(self, clinic_id, since, until=None):
        coming_visits = self.client.get_coming_visits(clinic_id, since, until)
        return self.update_local_coming_visits(coming_visits)
    
    def update_local_coming_visits(self, visits):
        # the clinic is part of the call to the RPC service, we specify it
        # so for the test we can also just specify one
        clinic = Clinic.objects.all()[0]
        for visit in visits:
            try:
                local_visit = get_object_or_none(Visit, te_visit_id=visit.key_id)
                if not local_visit:
                    local_visit = Visit.objects.create(te_id=visit.te_id, 
                        te_visit_id=visit.key_id,
                        clinic=clinic,
                        patient=Patient.objects.get(te_id=visit.te_id),
                        date=iso8601.parsedate(visit.date)
                    )
                print local_visit
                yield local_visit
            except IntegrityError, e:
                logger.exception('Failed to create')