from django.contrib.auth.models import User

class PatientBackend(object):
    def authenticate(self, msisdn, patient_id):
        patient = Patient.objects.get(msisdn=msisdn, te_id=patient_id)
        return patient