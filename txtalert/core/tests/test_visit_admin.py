from uuid import uuid4
from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User, Group

from txtalert.core.models import Visit, Clinic, Patient, MSISDN
from txtalert.core.clinic_admin import VisitAdmin


class VisitAdminTestCase(TestCase):

    def setUp(self):

        self.admin_user = User.objects.create_superuser(
            'admin', 'admin@admin.com', password='admin')

        self.clinic_group1 = Group.objects.create(name='clinic group 1')
        self.clinic_user1 = User.objects.create_user(
            'clinic1', 'clinic1@clinic1.com', password='clinic1')
        self.clinic_user1.groups = [self.clinic_group1]
        self.clinic_user1.save()

        self.clinic1 = Clinic.objects.create(
            name='Clinic 1', user=self.clinic_user1, te_id=uuid4().hex)

        self.clinic_group2 = Group.objects.create(name='clinic group 2')
        self.clinic_user2 = User.objects.create_user(
            'clinic2', 'clinic2@clinic2.com', password='clinic2')
        self.clinic_user2.groups = [self.clinic_group2]
        self.clinic_user2.save()

        self.clinic2 = Clinic.objects.create(
            name='Clinic 2', user=self.clinic_user2, te_id=uuid4().hex)

        self.site = AdminSite()
        self.visit_admin = VisitAdmin(Visit, self.site)

    def create_patients(self, count=10):
        patients = []
        for i in range(count):
            clinic = (self.clinic1 if i % 2 else self.clinic2)
            patient_id = 'patient-%s' % (i,)
            msisdn = '2700000000%s' % (i,)
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
        print patient
        return patient

    def create_visits(self, patient, clinic, count=10):
        visits = []
        for i in range(count):
            visit_date = (datetime.now() - timedelta(days=count/2) +
                          timedelta(days=i))
            visit = Visit.objects.create(
                patient=patient, te_visit_id=uuid4().hex, date=visit_date,
                status=('a' if visit_date.date() < datetime.now().date()
                        else 's'),
                clinic=clinic)
            visits.append(visit)
        return visits

    def test_querysetfilter(self):
        self.assertTrue(1)
