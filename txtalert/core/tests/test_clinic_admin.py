from uuid import uuid4
from datetime import datetime, timedelta

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User, Group
from django.test import TestCase, RequestFactory

from txtalert.core.models import Visit, Clinic, Patient, MSISDN
from txtalert.core.clinic_admin import VisitAdmin, PatientAdmin


class ClinicAdminTestCase(TestCase):

    model_class = None
    model_admin_class = None

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            'admin', 'admin@admin.com', password='admin')

        self.clinic1_group = Group.objects.create(name='clinic group 1')
        self.clinic1_user = User.objects.create_user(
            'clinic1', 'clinic1@clinic1.com', password='clinic1')
        self.clinic1_user.groups = [self.clinic1_group]
        self.clinic1_user.save()

        self.clinic1 = Clinic.objects.create(
            name='Clinic 1', user=self.clinic1_user, te_id=uuid4().hex)

        self.clinic2_group = Group.objects.create(name='clinic group 2')
        self.clinic2_user = User.objects.create_user(
            'clinic2', 'clinic2@clinic2.com', password='clinic2')
        self.clinic2_user.groups = [self.clinic2_group]
        self.clinic2_user.save()

        self.clinic2 = Clinic.objects.create(
            name='Clinic 2', user=self.clinic2_user, te_id=uuid4().hex)

        self.site = AdminSite()
        self.model_admin = self.model_admin_class(self.model_class, self.site)

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
            visit_date = (datetime.now() - timedelta(days=count/2) +
                          timedelta(days=i))
            visit = Visit.objects.create(
                patient=patient, te_visit_id=uuid4().hex, date=visit_date,
                status=('a' if visit_date.date() < datetime.now().date()
                        else 's'),
                clinic=clinic)
            visits.append(visit)
        return visits


class VisitAdminTestCase(ClinicAdminTestCase):

    model_class = Visit
    model_admin_class = VisitAdmin

    def test_clinic_queryset_filter(self):
        clinic1_patients = [p.te_id for p in
                            self.create_patients(self.clinic1, count=2)]
        clinic2_patients = [p.te_id for p in
                            self.create_patients(self.clinic2, count=2)]

        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.clinic1_user
        request.session = {}

        self.assertTrue(all([v.patient.te_id in clinic1_patients for v in
                             self.model_admin.queryset(request)]))
        self.assertFalse(any([v.patient.te_id in clinic2_patients for v in
                             self.model_admin.queryset(request)]))

    def test_superuser_queryset(self):
        clinic1_patients = self.create_patients(self.clinic1, count=2)
        clinic2_patients = self.create_patients(self.clinic2, count=2)
        all_patients = set([
            p.te_id for p in (clinic1_patients + clinic2_patients)])

        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.admin_user
        request.session = {}

        self.assertEqual(
            all_patients,
            set([v.patient.te_id for v in self.model_admin.queryset(request)]))

    def test_clinic_user_form_listing(self):
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.clinic1_user
        request.session = {}

        form = self.model_admin.get_form(request)()
        self.assertTrue("Clinic 1" in str(form['clinic']))
        self.assertFalse("Clinic 2" in str(form['clinic']))


class PatientAdminTestCase(ClinicAdminTestCase):

    model_class = Patient
    model_admin_class = PatientAdmin

    def test_patient_queryset_filter(self):
        clinic1_patients = [p.te_id for p in
                            self.create_patients(self.clinic1, count=2)]
        clinic2_patients = [p.te_id for p in
                            self.create_patients(self.clinic2, count=2)]

        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.clinic1_user
        request.session = {}

        self.assertTrue(all([patient.te_id in clinic1_patients for patient in
                             self.model_admin.queryset(request)]))
        self.assertFalse(any([patient.te_id in clinic2_patients for patient in
                             self.model_admin.queryset(request)]))

    def test_superuser_queryset(self):
        clinic1_patients = self.create_patients(self.clinic1, count=2)
        clinic2_patients = self.create_patients(self.clinic2, count=2)
        all_patients = set([
            p.te_id for p in (clinic1_patients + clinic2_patients)])

        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.admin_user
        request.session = {}

        self.assertEqual(
            all_patients,
            set([patient.te_id for patient in
                 self.model_admin.queryset(request)]))

    def test_clinic_save_model(self):

        [patient] = self.create_patients(self.clinic1, count=1)
        self.assertEqual(patient.owner, self.clinic1.user)

        other_clinic1_user = User.objects.create_user(
            'otherclinic1', 'otherclinic1@clinic1.com',
            password='otherclinic1')
        other_clinic1_user.groups = [self.clinic1_group]
        other_clinic1_user.save()

        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = other_clinic1_user
        request.session = {}

        self.model_admin.save_model(request, patient, None, None)

        patient = Patient.objects.get(pk=patient.pk)
        self.assertEqual(patient.owner, other_clinic1_user)

    def test_superuser_save_model(self):

        [patient] = self.create_patients(self.clinic1, count=1)
        self.assertEqual(patient.owner, self.clinic1.user)

        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.admin_user
        request.session = {}

        self.model_admin.save_model(request, patient, None, None)

        patient = Patient.objects.get(pk=patient.pk)
        self.assertEqual(patient.owner, self.clinic1.user)
