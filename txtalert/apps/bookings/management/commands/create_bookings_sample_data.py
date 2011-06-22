from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from txtalert.core.models import (Patient, Clinic, MSISDN, 
                                    VISIT_STATUS_CHOICES, Visit)
from optparse import make_option
from datetime import datetime, timedelta
import random
import sys
from uuid import uuid1

def sample(items):
    return random.sample(items, 1).pop()

NAMES = ['Aaliyah', 'Abayomi', 'Abebe', 'Abebi', 'Abena', 'Abeo', 'Ada', 
            'Adah', 'Adana', 'Adanna', 'Adanya', 'Akili', 'Alika', 'Ama', 
            'Amadi', 'Amai', 'Amare', 'Amari', 'Abayomi', 'Abiola', 'Abu', 
            'Ade', 'Adeben', 'Adiel', 'Amarey', 'Amari', 'Aren', 'Azibo', 
            'Bobo', 'Chiamaka', 'Chibale', 'Chidi', 'Chike', 'Dakarai', 
            'Davu', 'Deion', 'Dembe', 'Diallo']
SURNAMES = ['Azikiwe','Awolowo','Bello','Balewa','Akintola','Okotie-Eboh',
            'Nzeogwu','Onwuatuegwu','Okafor','Okereke','Okeke','Okonkwo',
            'Okoye','Okorie','Obasanjo','Babangida','Buhari','Dimka','Okar',
            'Diya','Odili','Ibori','Igbinedion','Alamieyeseigha','Yar\'Adua',
            'Asari-Dokubo','Jomo-Gbomo','Anikulapo-Kuti','Iwu','Anenih',
            'Bamgboshe','Biobaku','Tinibu','Akinjide','Akinyemi','Akiloye',
            'Adeyemi','Adesida','Omehia','Sekibo','Amaechi','Bankole','Nnamani',
            'Ayim','Okadigbo','Ironsi','Ojukwu','Danjuma','Effiong','Akpabio',
            'Attah','Chukwumereije','Akunyili','Iweala','Okonjo','Ezekwesili',
            'Achebe','Soyinka','Solarin','Gbadamosi','Olanrewaju','Magoro',
            'Madaki','Jang','Oyinlola','Oyenusi','Onyejekwe','Onwudiwe',
            'Jakande','Kalejaiye','Igwe','Eze','Obi','Ngige','Uba','Kalu',
            'Orji','Ohakim','Egwu','Adesina','Adeoye','Falana','Fagbure',
            'Jaja','Okilo','Okiro','Balogun','Alakija','Akenzua','Akerele',
            'Ademola','Onobanjo','Aguda','Okpara','Mbanefo','Mbadinuju','Boro',
            'Ekwensi','Gowon', 'Saro-Wiwa']

class Command(BaseCommand):
    help = "Generate sample data to populate a new installation " \
            "of txtAlert:bookings for demo purposes"
    option_list = BaseCommand.option_list + (
        make_option('--owner', dest='owner', help='Who should own these patients?'),
        make_option('--patients', default=50, dest='patients',
            help='How many patients to create'),
        make_option('--visits', default=100, dest='visits',
            help='How many visits to create per patient'),
        make_option('--change-requests', default=1, dest='change_requests',
            help='How many change requests to create per visit')
    )
    
    def handle(self, *args, **options):
        if options.get('owner'):
            self.owner = User.objects.get(username=options['owner'])
        else:
            print 'Please provide --owner=<username>'
            sys.exit(1)
        
        self.clinics = Clinic.objects.all()
        for patient in self.create_patients(int(options['patients'])):
            visits = list(self.create_visits(patient, int(options['visits'])))
            list(self.create_change_requests(visits, int(options['change_requests'])))
    
    def create_patients(self, limit):
        for i in range(limit):
            msisdn, _ = MSISDN.objects.get_or_create(msisdn=(27761000000 + i))
            print 'patient %s of %s' % (i,limit)
            yield Patient.objects.create(
                name = sample(NAMES),
                surname = sample(SURNAMES),
                owner = self.owner,
                te_id = 'bookings-%s' % Patient.objects.count(),
                active_msisdn = msisdn,
                regiment = sample(Patient.REGIMENT_CHOICES)[0],
                sex = sample(['m','f']),
                age = i,
                last_clinic = sample(self.clinics),
            )
    
    def create_visits(self, patient, limit):
        for i in range(limit):
            date = datetime.now() + timedelta(days=((-1 * i)+10))
            if date < datetime.now():
                status = sample(VISIT_STATUS_CHOICES)[0]
            else:
                status = 's'
            
            yield patient.visit_set.create(
                te_visit_id = 'visit-%s' % Visit.objects.count(),
                date = date,
                status = status,
                visit_type = sample(Visit.VISIT_TYPES)[0],
                clinic = patient.last_clinic
            )
    
    def create_change_requests(self, visits, limit):
        visits = list(visits)
        for i in range(limit):
            request = sample(['earlier','later'])
            visit = visits.pop()
            fn = getattr(visit, 'reschedule_%s' % request)
            yield fn()
