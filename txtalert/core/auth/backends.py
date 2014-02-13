from base64 import b64decode
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from txtalert.core.models import Patient, AuthProfile
from txtalert.core.utils import normalize_msisdn


class PatientBackend(ModelBackend):
    def authenticate(self, username, password):
        try:
            # get the msisdn
            msisdn, patient_id = normalize_msisdn(username), password
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
        except ValueError, e:
            # normalize_msisdn raised an error, probably a regular string
            # was passed in which it tried to convert to an integer
            pass


class HttpBasicAuthBackend(ModelBackend):

    def authenticate(self, remote_user):
        b64str = remote_user[6:]
        username, password = b64decode(b64str).split(':')
        return super(HttpBasicAuthBackend, self).authenticate(
            username=username, password=password)
