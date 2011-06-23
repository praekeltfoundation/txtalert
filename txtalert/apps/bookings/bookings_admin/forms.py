from django import forms
from django.forms.widgets import RadioSelect
from django.forms.extras.widgets import SelectDateWidget
from txtalert.core.utils import normalize_msisdn
from txtalert.core.models import Patient, MSISDN, Visit, Clinic

class MSISDNForm(forms.Form):
    msisdn = forms.CharField(min_length=10, required=True, 
                help_text='What is your phone number?',
                error_messages={'required': 'Please provide a valid phone number.'})    
    def clean_msisdn(self):
        raw_msisdn = self.cleaned_data['msisdn']
        return normalize_msisdn(raw_msisdn)

class PatientForm(forms.ModelForm):
    name = forms.CharField(required=True)
    surname = forms.CharField(required=True)
    active_msisdn = forms.CharField(label='Phone Number', required=True, 
        min_length=10)
    
    def clean_active_msisdn(self):
        raw_msisdn = self.cleaned_data['active_msisdn']
        msisdn, created = MSISDN.objects.get_or_create(
            msisdn=normalize_msisdn(raw_msisdn))
        return msisdn
    
    class Meta:
        model = Patient
        fields = [
            'name',
            'surname',
            'language',
            'sex',
            'age',
            'active_msisdn',
            'regiment',
            'last_clinic',
            'disclosed',
            'opted_in',
        ]

class VisitForm(forms.ModelForm):
    clinic = forms.ModelChoiceField(label='At which clinic?', required=True,
        queryset=Clinic.objects.all())
    visit_type = forms.ChoiceField(label='Appointment type', required=True, 
        choices=Visit.VISIT_TYPES)
    comment = forms.CharField(label='Appointment notes', 
        widget=forms.Textarea(attrs={'rows':2}), required=False)
    
    class Meta:
        model = Visit
        fields = [
            'clinic',
            'visit_type',
            'comment',
        ]

class EditVisitForm(forms.ModelForm):
    clinic = forms.ModelChoiceField(label='At which clinic?', required=True,
        queryset=Clinic.objects.all())
    visit_type = forms.ChoiceField(label='Appointment type', required=True, 
        choices=Visit.VISIT_TYPES)
    comment = forms.CharField(label='Appointment notes', 
        widget=forms.Textarea(attrs={'rows':2}), required=False)
    date = forms.DateField(label='Date', required=True, 
        widget=SelectDateWidget())
    
    class Meta:
        model = Visit
        fields = [
            'clinic',
            'visit_type',
            'status',
            'comment',
            'date',
        ]

class SimpleDateForm(forms.Form):
    date = forms.DateField(label='Pick Another Date:', required=True,
        widget=SelectDateWidget())