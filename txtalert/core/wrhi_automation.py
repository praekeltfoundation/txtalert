from txtalert.core.models import Patient, ClinicNameMapping
import requests
import logging

logger = logging.getLogger(__name__)


def fetch_visit_data(endpoint):
    pass


def import_visits(endpoint):
    pass


def fetch_patient_data(endpoint):
    url = endpoint + '/patientlist'
    result = requests.get(url)

    if result.status_code == 200:
        return result.json()
    else:
        result.raise_for_staus()


def map_clinic(clinic_name):
    clinic_map = ClinicNameMapping.objects.select_related().filter(wrhi_clinic_name__iexact=clinic_name).first()

    if clinic_map:
        return clinic_map.clinic.name
    else:
        return None


def update_patient(clinic, patient):
    # firstly lets find the clinic in the mapping
    pass


def import_patients(endpoint):
    data = fetch_patient_data(endpoint)

    for clinic in data:

        if 'Facility_name' in clinic:

            wrhi_clinic_name = clinic['Facility_name']
            clinic_name = map_clinic(wrhi_clinic_name)

            if clinic_name:
                if 'Patients' in clinic:
                    patients = clinic['Patients']

                    for patient in patients:
                        update_patient(clinic_name, patient)

                else:
                    logger.warn('import_patients clinic %s has no Patients'
                                % clinic_name)
            else:
                logger.warn('import_patients clinic mapping failed for'
                            'wrhi clinic %s' % wrhi_clinic_name)

        else:
            logger.warn('import_patients clinic found without a Facility_name')


#import_patients('http://10.0.0.4:62489/api/appad')