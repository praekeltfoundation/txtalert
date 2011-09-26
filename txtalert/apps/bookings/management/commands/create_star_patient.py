from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from txtalert.core.models import (Patient, Clinic, MSISDN, 
                                    VISIT_STATUS_CHOICES, Visit)
from optparse import make_option
from datetime import datetime, timedelta
import sys

class Command(BaseCommand):
    help = "Generate flat pages required for txtAlert:bookings"
    option_list = BaseCommand.option_list + (
        make_option('--patient-id', dest='patient_id', help='How many patients to create'),
        make_option('--clinic', dest='clinic', help='Which clinic should the patient attend?'),
    )
    def handle(self, *args, **options):
        patient_id = options['patient_id']
        clinic = options['clinic']
        if not patient_id:
            print 'Please provided a --patient-id'
            sys.exit(1)
        if not clinic:
            print 'Please provide a --clinic'
            sys.exit(1)

        
        patient = Patient.objects.get(te_id=patient_id)
        clinic = Clinic.objects.get(name=clinic)
        last_year = datetime.today() - timedelta(days=365)
        for i in range(20):
            date = last_year + timedelta(days=(i*28))
            if date < datetime.today():
                if i == 12:
                    status = 'm'
                else:
                    status = 'a'
            else:
                if i == 14:
                    status = 'r'
                else:
                    status = 's'
            
            patient.visit_set.create(
                clinic=clinic,
                status=status,
                date=date,
                visit_type='arv',
                te_visit_id = 'visit-%s' % Visit.objects.count()+1
            )
            
        