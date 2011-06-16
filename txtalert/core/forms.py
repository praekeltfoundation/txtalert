from django import forms
from txtalert.core.models import Clinic

class RequestCallForm(forms.Form):
    clinic = forms.ModelChoiceField(queryset=Clinic.objects.all(), 
                required=True, help_text='Which clinic do you want to receive a call from?', 
                error_messages={'required': 'Please select a clinic.'})
    msisdn = forms.CharField(min_length=10, required=True, 
                help_text='What number can we reach you on?',
                error_messages={'required': 'Please provide a valid phone number.'})