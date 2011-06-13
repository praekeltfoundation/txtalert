from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from txtalert.core.models import Patient, AuthProfile

class PatientBackend(ModelBackend):
    def authenticate(self, username, password):
        msisdn, patient_id = username, password
        try:
            # try and find the patient
            patient = Patient.objects.get(active_msisdn__msisdn=msisdn, te_id=patient_id)
            try:
                return patient.authprofile.user
            except AuthProfile.DoesNotExist, e:
                user = User(username=msisdn)
                user.set_password(patient_id)
                user.save()
                AuthProfile.objects.create(user=user, patient=patient)
                return user
        except Patient.DoesNotExist, e:
            pass