from txtalert.core.models import Patient, ClinicNameMapping, MSISDN, Visit
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from datetime import datetime, timedelta
from dateutil.parser import parse as date_util_parse
from txtalert.apps.general.settings.models import Setting
import requests
import logging
import re
import traceback

logger = logging.getLogger(__name__)

COMING_VISIT = 1
MISSED_VISIT = 2
DONE_VISIT = 3


class VisitInc:
    ptd_no = None
    visit = None
    return_date = None
    visit_date = None
    status = None
    file_no = None
    cellphone_number = None
    facility_name = None
    next_tcb = None

    def __init__(self, sobj):
        if 'Ptd_No' in sobj:
            self.ptd_no = sobj['Ptd_No']

        if 'Visit' in sobj:
            self.visit = sobj['Visit']

        if 'Return_date' in sobj:
            self.return_date = sobj['Return_date']

        if 'Visit_date' in sobj:
            self.visit_date = sobj['Visit_date']

        if 'Status' in sobj:
            self.status = sobj['Status']

        if 'File_No' in sobj:
            self.file_no = sobj['File_No']

        if 'Cellphone_number' in sobj:
            self.cellphone_number = sobj['Cellphone_number']

        if 'Facility_name' in sobj:
            self.facility_name = sobj['Facility_name']

        if 'Next_tcb' in sobj:
            self.next_tcb = sobj['Next_tcb']

    @staticmethod
    def _get_date(d):
        if d:
            if type(d) == datetime:
                return d

            try:
                return date_util_parse(d)
            except (ValueError, OverflowError):
                return None
        else:
            return None

    def get_visit_date(self):
        d = self._get_date(self.visit_date)
        if d:
            self.visit_date = d

        return d

    def get_next_tcb(self):
        d = self._get_date(self.next_tcb)

        if d:
            self.next_tcb = d

        return d

    def get_return_date(self):
        d = self._get_date(self.return_date)

        if d:
            self.return_date = d

        return d


def map_clinic(clinic_name):
    clinic_map = ClinicNameMapping.objects.select_related().filter(wrhi_clinic_name__iexact=clinic_name).first()

    if clinic_map:
        return clinic_map
    else:
        return None


def fetch_visit_data(endpoint, visit_type):
    if visit_type == COMING_VISIT:
        func = 'ComingVisits'
    elif visit_type == MISSED_VISIT:
        func = 'MissedVisits'
    elif visit_type == DONE_VISIT:
        func = 'DoneVisits'
    else:
        raise Exception('Incorrect type specified expecting 1,2 or 3 got %s'
                        % visit_type)

    date_now = datetime.now()
    three_weeks = timedelta(weeks=3)
    date_from = date_now - three_weeks
    date_to = date_now + three_weeks

    logger.info('Fetch %s data for %s - %s' % (func, date_from, date_to))

    url = endpoint + '/' + func + \
        '?dateFrom=' + date_from.strftime('%Y_%m_%d') + \
        '&dateTo=' + date_to.strftime('%Y_%m_%d')

    result = requests.get(url)

    if result.status_code == 200:
        return result.json()
    else:
        result.raise_for_status()


def check_orig_date(patient, clinic, date):
    # Check to see if the new
    visits = Visit.objects.filter(
        patient=patient,
        clinic=clinic,
        wrhi_orig_date=date)

    if visits is not None and visits.count() == 0:
        return True
    else:
        return False


def create_visit(patient, clinic, date=None, status=None):
    kwargs = {
        'patient': patient,
        'clinic': clinic
    }

    if date:
        kwargs['date'] = date

    visits = Visit.objects.filter(**kwargs)

    if status:
        kwargs['status'] = status

    kwargs['wrhi_orig_date'] = date

    if check_orig_date(patient, clinic, date):
        if visits is not None and visits.count() == 0:
            v = Visit.objects.create(
                **kwargs
            )
            logger.info("Visit created.")
            return v

    return visits


@transaction.atomic
def process_visit(v, visit_type):
    """
    :param v: VisitInc
    :param visit_type:
    :return:
    """
    try:
        with transaction.atomic():
            if v.ptd_no is None:
                logger.warning('wrhi_automation::process_visit: Visit has no '
                               'Ptd_No - skipping visit')
                return

            # find the patient
            db_patient = Patient.all_objects.filter(te_id=v.ptd_no).first()

            if db_patient is None:
                logger.warning('wrhi_automation::process_visit: Can''t find '
                               'Patient with Ptd_No %s - skipping visit'
                               % v.ptd_no)
                return

            if db_patient.deleted:
                logger.warning('wrhi_automation::process_visit: Patient '
                               'with Ptd_No %s has been deleted - '
                               'skipping visit' % v.ptd_no)
                return

            # get the clinic
            db_clinic = map_clinic(v.facility_name)

            if db_clinic is None:
                logger.warning('wrhi_automation::process_visit: Clinic mapping'
                               ' failed for wrhi clinic %s - skipping visit'
                               % v.facility_name)
                return

            # get the current visits for this patient at the specified clinic
            visits = Visit.objects.filter(patient=db_patient, clinic=db_clinic.clinic)
            found_visit = False

            if visits:
                if visit_type == COMING_VISIT:
                    search_date = v.get_visit_date()

                    if search_date is None:
                        search_date = v.get_next_tcb()
                else:
                    search_date = v.get_visit_date()

                if search_date is None:
                    logger.warning('wrhi_automation::process_visit: '
                                   'search_date is empty for Visit Type %s '
                                   'and Ptd_no %s - skipping visit'
                                   % (visit_type, v.ptd_no))
                    return

                search_date = search_date.date()

                for visit in visits:
                    if visit.date == search_date:
                        found_visit = True

                        if visit_type == COMING_VISIT:
                            # check if the next_tcb visit has been created already
                            next_visit_date = v.get_next_tcb()

                            if next_visit_date:
                                logger.info("Attempting to create visit for %s @ %s on %s"
                                            % (db_patient.te_id, db_clinic.clinic.name, next_visit_date))
                                create_visit(
                                    patient=db_patient,
                                    date=next_visit_date,
                                    clinic=db_clinic.clinic,
                                    status='s'
                                )
                        elif visit_type == MISSED_VISIT:
                            # only update it once
                            if visit.status != 'm':
                                # update the visit status
                                visit.status = 'm'
                                visit.save()

                                res_date = v.get_next_tcb()

                                # create a new visit for the reschedule
                                if res_date:
                                    logger.info("Attempting to create visit for %s @ %s on %s"
                                                % (db_patient.te_id, db_clinic.clinic.name, res_date))
                                    create_visit(
                                        patient=db_patient,
                                        date=res_date,
                                        clinic=db_clinic.clinic,
                                        status='s'
                                    )
                        elif visit_type == DONE_VISIT:
                            if visit.status != 'a':
                                # update the visit status
                                visit.status = 'a'

                                # if the patient attended early adjust the internal
                                # visit date
                                if v.status.lower() == 'ae':
                                    return_date = v.get_return_date()

                                    if return_date:
                                        visit.date = return_date

                                visit.save()

                                next_visit_date = v.get_next_tcb()

                                if next_visit_date:
                                    # create a new visit for the next_tcb date
                                    logger.info("Attempting to create visit for %s @ %s on %s"
                                                % (db_patient.te_id, db_clinic.clinic.name, next_visit_date))
                                    create_visit(
                                        patient=db_patient,
                                        date=next_visit_date,
                                        clinic=db_clinic.clinic,
                                        status='s'
                                    )

            if not found_visit:
                if visit_type == COMING_VISIT:
                    visit_date = v.get_visit_date()
                    visit_date2 = v.get_next_tcb()

                    if visit_date is None:
                        visit_date = visit_date2

                else:
                    visit_date = v.get_visit_date()

                vt = None

                if visit_type == COMING_VISIT:
                    vt = 's'
                elif visit_type == MISSED_VISIT:
                    vt = 'm'
                elif visit_type == DONE_VISIT:
                    vt = 'a'

                logger.info("Attempting to create visit for %s @ %s on %s"
                            % (db_patient.te_id, db_clinic.clinic.name, visit_date))

                create_visit(
                    patient=db_patient,
                    date=visit_date,
                    clinic=db_clinic.clinic,
                    status=vt
                )

                if visit_type == COMING_VISIT and visit_date2:
                    # because the query in COMING_VISITS looks at visit_date
                    # and next_tcb we might have two none existing visits
                    logger.info("Attempting to create visit for %s @ %s on %s"
                                % (db_patient.te_id, db_clinic.clinic.name, visit_date2))
                    create_visit(
                        patient=db_patient,
                        date=visit_date2,
                        clinic=db_clinic.clinic,
                        status=vt
                    )

    except Exception:
        logger.warning('wrhi_automation::process_visit: Failed to process '
                       'visit of type %s for Ptd_No %s Clinic %s. '
                       'Reason : %s'
                       % (visit_type, v.ptd_no, v.facility_name, traceback.format_exc()))


def import_visits(endpoint):
    logger.info('wrhi_automation::import_visits: Started')
    owner = User.objects.filter(username=settings.WRHI_IMPORT_USER).first()

    if owner is None:
        logger.error('Configuration error. WRHI_IMPORT_USER has not been set')
        return

    data = None

    try:
        data = fetch_visit_data(endpoint, COMING_VISIT)
    except Exception as ex:
        logger.warning('wrhi_automation::import_visits: Failed to fetch '
                       'coming visit data. Reason: %s' % ex)

    if data:
        for row in data:
            process_visit(VisitInc(row), COMING_VISIT)

    try:
        data = fetch_visit_data(endpoint, MISSED_VISIT)
    except Exception as ex:
        logger.warning('wrhi_automation::import_visits: Failed to fetch '
                       'missed visit data. Reason: %s' % ex)

    if data:
        for row in data:
            process_visit(VisitInc(row), MISSED_VISIT)

    try:
        data = fetch_visit_data(endpoint, DONE_VISIT)
    except Exception as ex:
        logger.warning('wrhi_automation::import_visits: Failed to fetch '
                       'done visit data. Reason: %s' % ex)

    if data:
        for row in data:
            process_visit(VisitInc(row), DONE_VISIT)

    logger.info('wrhi_automation::import_visits: Completed')


def fetch_patient_data(endpoint):
    url = endpoint + '/patientlist'
    result = requests.get(url)

    if result.status_code == 200:
        return result.json()
    else:
        result.raise_for_status()


@transaction.atomic
def update_patient(clinic, patient, owner_user, wrhi_msisdn_override):
    ptd_no = None
    mobiles = None

    try:
        with transaction.atomic():
            if 'Ptd_No' in patient:
                ptd_no = patient['Ptd_No']

            if 'Cellphone_number' in patient:
                if wrhi_msisdn_override:
                    temp_str = wrhi_msisdn_override
                else:
                    temp_str = patient['Cellphone_number']
                mobiles = re.split(r'[\\,/;]', temp_str)

            if ptd_no and mobiles and len(mobiles) > 0:
                db_patient = Patient.all_objects.filter(te_id=ptd_no).first()

                if db_patient and db_patient.deleted:
                    logger.info('Patient %s has been deleted, skipping patient' % ptd_no)
                    return

                if db_patient is None:
                    db_patient = Patient.objects.create(te_id=ptd_no, owner=owner_user, last_clinic=clinic.clinic)
                    logger.info("Patient %s has been created in %s clinic" % (ptd_no, clinic.clinic.name))

                count = 0

                for mobile in mobiles:
                    db_mobile = MSISDN.objects.filter(msisdn=mobile).first()

                    if db_mobile is None:
                        db_mobile = MSISDN.objects.create(msisdn=mobile)
                        logger.info("MSISDN %s created" % mobile)

                    if db_mobile not in db_patient.msisdns.all():
                        db_patient.msisdns.add(db_mobile)
                        logger.info("MSISDN %s assigned to patient %s" %(db_mobile.msisdn, ptd_no))

                    if count == 0 and db_patient.active_msisdn is None:
                        db_patient.active_msisdn = db_mobile
                        logger.info("MSISDN %s marked as active for patient %s" % (db_mobile.msisdn, ptd_no))

                    db_patient.save()
                    count += 1

    except Exception as ex:
        logger.warning('wrhi_automation::update_patient: Failed to update '
                       'patient %s from clinic %s. Reason: %s'
                       % (ptd_no, clinic.clinic.name, ex))


def import_patients(endpoint):
    logger.info('wrhi_automation::import_patients: Started')
    try:
        data = fetch_patient_data(endpoint)
    except Exception as ex:
        logger.warning('wrhi_automation::import_patients: Failed to fetch '
                       'patient data. Reason: %s' % ex)
        return

    owner = User.objects.filter(username=settings.WRHI_IMPORT_USER).first()

    # Check for sepcial QA setting
    s = Setting.objects.filter(name='WRHI_MSISDN_OVERRIDE').first()
    wrhi_msisdn_override = None

    if s:
        wrhi_msisdn_override = s.text_value

    if owner is None:
        logger.error('Configuration error. WRHI_IMPORT_USER has not been set')
        return

    for clinic in data:

        if 'Facility_name' in clinic:

            wrhi_clinic_name = clinic['Facility_name']
            db_clinic = map_clinic(wrhi_clinic_name)

            if db_clinic:
                if 'Patients' in clinic:
                    patients = clinic['Patients']

                    for patient in patients:
                        update_patient(db_clinic, patient, owner, wrhi_msisdn_override)

                else:
                    logger.warning('import_patients clinic %s has no Patients'
                                   % wrhi_clinic_name)
            else:
                logger.warning('import_patients clinic mapping failed for'
                               'wrhi clinic %s' % wrhi_clinic_name)

        else:
            logger.warning('import_patients clinic found without a Facility_name')

    logger.info('wrhi_automation::import_patients: Completed')