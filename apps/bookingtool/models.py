from django.db import models
from therapyedge.models import Patient, Visit
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
        return self.visit_set.filter(date__gte=midnight)
    
    def determine_year_of_birth(self):
        year_of_birth = datetime.now().year - self.age
        return datetime(day=1, month=1, year=year_of_birth)
    
    def save(self, *args, **kwargs):
        """If the date_of_birth isn't set, we automatically pin the date of 
        birth based on the year, assuming the 1st of january."""
        if not self.date_of_birth:
            self.date_of_birth = self.determine_year_of_birth()
        
        """If the patient was opted in and our opt_status hasn't been set yet
        automatically set it to 'opt-in' based on the patient record"""
        if self.opted_in and not self.opt_status:
            self.opt_status = 'opt-in'
        
        """and the other way around as well"""
        if self.opt_status == 'opt-in' and not self.opted_in:
            self.opted_in = True
        
        return super(Patient, self).save(*args, **kwargs)

