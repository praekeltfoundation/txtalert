from django import forms
from django.forms.widgets import RadioSelect
from txtalert.core.utils import normalize_msisdn
from txtalert.core.models import Patient, MSISDN

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
    regiment = forms.ChoiceField(label='Treatment Cycle', choices=(
        ('1', '1 month'),
        ('3', '3 months'),
        ('6', '6 months'),
    ))
    
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
