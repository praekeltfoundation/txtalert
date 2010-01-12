from django.db import models
from django.db.models.signals import pre_save
from txtalert.core.models import Patient, Visit
from bookingtool import signals
from datetime import datetime

class BookingPatient(Patient):
    
    OPT_STATUSES = (
        ('not-yet', 'Not yet opted in to TxtAlert'),
        ('opt-in', 'Opt in to TxtAlert'),
        ('opt-out', 'Opt out of TxtAlert'),
        ('ltfu', 'Lost to follow up at 30 days'),
        ('presumed-dead', 'Presumed dead'),
        ('confirmed-dead', 'Confirmed dead'),
    )
    
    TREATMENT_CYCLES = (
        (1, 'one month cycle'),
        (2, 'two month cycle'),
        (3, 'three month cycle'),
    )
    
    name = models.CharField('First name', blank=True, max_length=80)
    surname = models.CharField('Surname', blank=True, max_length=80)
    date_of_birth = models.DateField('Date of Birth', blank=True, null=True, auto_now_add=False)
    opt_status = models.CharField(blank=True, max_length=20, choices=OPT_STATUSES)
    treatment_cycle = models.IntegerField(blank=False, null=True, choices=TREATMENT_CYCLES, default=1)
    
    @property
    def appointments(self):
        midnight = datetime.now().date()
        return Visit.objects.filter(patient=self, date__gte=midnight)
    
    def determine_year_of_birth(self):
        year_of_birth = datetime.now().year - self.age
        return datetime(day=1, month=1, year=year_of_birth)
    

pre_save.connect(
    receiver=signals.pre_save_booking_patient_handler, 
    sender=BookingPatient
)