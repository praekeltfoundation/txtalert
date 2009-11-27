from django.db import IntegrityError
from therapyedge.xmlrpc.client import Client
from therapyedge.models import Patient, MSISDN

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


class Importer(object):
    
    def __init__(self, uri=None, verbose=False):
        self.client = Client(uri, verbose)

    def import_all_patients(self, clinic_id):
        all_patients = self.client.get_all_patients(clinic_id)
        # not sure what to do here yet since this one either fails or returns
        # an empty list
    
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
        return self.update_local_visits(coming_visits)
    
    def update_local_visits(self, visits):
        for visit in visits:
            try:
                pass # left off here
            except IntegrityError, e:
                logger.exception('Failed to create')