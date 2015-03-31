from txtalert.core.models import Patient, ClinicNameMapping, MSISDN
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from datetime import datetime, timedelta
import requests
import logging
import re

logger = logging.getLogger(__name__)


def map_clinic(clinic_name):
    clinic_map = ClinicNameMapping.objects.select_related().filter(wrhi_clinic_name__iexact=clinic_name).first()

    if clinic_map:
        return clinic_map
    else:
        return None


def fetch_visit_data(endpoint, type):
    # type: 1 - coming visits, 2 - missed visits, 3 - done visits
    func = None

    if type == 1:
        func = 'ComingVisits'
    elif type == 2:
        func = 'MissedVisits'
    elif type == 3:
        func = 'DoneVisits'
    else:
        raise Exception('Incorrect type specified expecting 1,2 or 3 got %s'
                        % type)

    date_now = datetime.now()
    three_weeks = timedelta(weeks=3)
    dateFrom = date_now - three_weeks
    dateTo = date_now + three_weeks

    url = endpoint + '/' + func + \
          '?dateFrom=' + dateFrom.strftime('%Y_%m_%d') + \
          '&dateTo=' + dateTo.strftime('%Y_%m_%d')

    result = requests.get(url)

    if result.status_code == 200:
        return result.json()
    else:
        result.raise_for_status()


def import_visits(endpoint):
    data = fetch_visit_data(endpoint, 1)
    data = fetch_visit_data(endpoint, 2)
    data = fetch_visit_data(endpoint, 3)
    owner = User.objects.filter(username=settings.WRHI_IMPORT_USER).first()

    if owner is None:
        logger.error('Configuration error. WRHI_IMPORT_USER has not been set')


def fetch_patient_data(endpoint):
    url = endpoint + '/patientlist'
    result = requests.get(url)

    if result.status_code == 200:
        return result.json()
    else:
        result.raise_for_status()


@transaction.atomic
def update_patient(clinic, patient, owner_user):
    ptd_no = None
    mobiles = None

    try:
        with transaction.atomic():
            if 'Ptd_No' in patient:
                ptd_no = patient['Ptd_No']

            if 'Cellphone_number' in patient:
                temp_str = patient['Cellphone_number']
                mobiles = re.split(r'[\\,/;]', temp_str)

            if ptd_no and mobiles and len(mobiles) > 0:
                db_patient = Patient.all_objects.filter(te_id=ptd_no).first()

                if db_patient and db_patient.deleted:
                    logger.info('Patient %s has been deleted, skipping patient' % ptd_no)
                    return

                if db_patient is None:
                    db_patient = Patient.objects.create(te_id=ptd_no, owner=owner_user)

                count = 0

                for mobile in mobiles:
                    db_mobile = MSISDN.objects.filter(msisdn=mobile).first()

                    if db_mobile is None:
                        db_mobile = MSISDN.objects.create(msisdn=mobile)

                    if db_mobile not in db_patient.msisdns.all():
                        db_patient.msisdns.add(db_mobile)

                    if count == 0 and db_patient.active_msisdn is None:
                        db_patient.active_msisdn = db_mobile

                    db_patient.save()
                    count += 1

    except Exception as ex:
        logger.warning('wrhi_automation::update_patient: Failed to update '
                       'patient %s from clinic %s. Reason: %s'
                       % (ptd_no, clinic.clinic.name, ex))


def import_patients(endpoint):
    data = fetch_patient_data(endpoint)
    owner = User.objects.filter(username=settings.WRHI_IMPORT_USER).first()

    if owner is None:
        logger.error('Configuration error. WRHI_IMPORT_USER has not been set')
    else:
        for clinic in data:

            if 'Facility_name' in clinic:

                wrhi_clinic_name = clinic['Facility_name']
                db_clinic = map_clinic(wrhi_clinic_name)

                if db_clinic:
                    if 'Patients' in clinic:
                        patients = clinic['Patients']

                        for patient in patients:
                            update_patient(db_clinic, patient, owner)

                    else:
                        logger.warn('import_patients clinic %s has no Patients'
                                    % wrhi_clinic_name)
                else:
                    logger.warn('import_patients clinic mapping failed for'
                                'wrhi clinic %s' % wrhi_clinic_name)

            else:
                logger.warn('import_patients clinic found without a Facility_name')