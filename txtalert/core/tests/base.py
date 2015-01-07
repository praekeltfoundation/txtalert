from uuid import uuid4
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from txtalert.core.models import Visit, Patient, MSISDN


class BaseTxtAlertTestCase(TestCase):

    def create_patients(self, clinic, count=10):
        patients = []
        for i in range(count):
            patient_id = uuid4().hex
            msisdn = '27%09d' % (MSISDN.objects.count(),)
            patient = self.create_patient(patient_id, msisdn, clinic.user)
            self.create_visits(patient, clinic)
            patients.append(patient)
        return patients

    def create_patient(self, patient_id, msisdn, owner):
        msisdn, _ = MSISDN.objects.get_or_create(msisdn=msisdn)
        patient = Patient.objects.create(
            te_id=patient_id, active_msisdn=msisdn, owner=owner)
        patient.msisdns = [msisdn]
        patient.save()
        return patient

    def create_visits(self, patient, clinic, count=10):
        visits = []
        for i in range(count):
            visit_date = (timezone.now() - timedelta(days=count/2) +
                          timedelta(days=i))
            visit = Visit.objects.create(
                patient=patient, te_visit_id=uuid4().hex, date=visit_date,
                status=('a' if visit_date.date() < timezone.now().date()
                        else 's'),
                clinic=clinic)
            visits.append(visit)
        return visits

    def create_missed_visit(self, patient, clinic):
        visit_date = (timezone.now() - timedelta(days=1)).date()
        return Visit.objects.create(
            patient=patient, te_visit_id=uuid4().hex, date=visit_date,
            status='m', clinic=clinic)

    def create_twoweek_visit(self, patient, clinic):
        visit_date = (timezone.now() + timedelta(days=14)).date()
        return Visit.objects.create(
            patient=patient, te_visit_id=uuid4().hex, date=visit_date,
            status='s', clinic=clinic)
