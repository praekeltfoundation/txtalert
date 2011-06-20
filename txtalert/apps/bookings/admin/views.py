from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.db.models import Q
from txtalert.apps.bookings.admin import forms
from txtalert.core.models import Patient
from txtalert.core.utils import normalize_msisdn
import logging

LOGIN_PERMISSION = 'core.add_patient'
LOGIN_URL = '/bookings/admin/sign-in/'

@permission_required(LOGIN_PERMISSION, login_url=LOGIN_URL)
def index(request):
    return render_to_response('admin/index.html', {},
        context_instance=RequestContext(request))

@permission_required(LOGIN_PERMISSION, login_url=LOGIN_URL)
def new_patient(request):
    if request.POST:
        form = forms.MSISDNForm(request.POST)
        if form.is_valid():
            msisdn = form.cleaned_data['msisdn']
            logging.error("Send SMS via VUMI to %s" % msisdn)
            messages.add_message(request, messages.INFO, 
                        'A verification SMS has been sent to %s.' % msisdn)
            
            return HttpResponseRedirect("%s?msisdn=%s" % (
                reverse('bookings:admin:new_patient_details'), msisdn))
    else:
        form = forms.MSISDNForm()
    return render_to_response("admin/patient/new.html", {
        'form': form
    }, context_instance=RequestContext(request))

@permission_required(LOGIN_PERMISSION, login_url=LOGIN_URL)
def new_patient_details(request):
    if request.POST:
        form = forms.PatientForm(request.POST)

        if form.is_valid():
            patient = form.save(commit=False)
            patient.owner = request.user
            # TODO: possible race condition
            patient.te_id = 'bookings-%s' % Patient.objects.count()
            patient.save()
            logging.debug('Created new patient: %s' % patient)
            messages.add_message(request, messages.INFO, 'Patient %(name)s '
                '%(surname)s registered' % form.cleaned_data)
            return HttpResponseRedirect(reverse('bookings:admin:index'))
        else:
            messages.add_message(request, messages.ERROR,
                'Registration failed. Please see errors below.')
    else:
        form = forms.PatientForm(initial={
            'active_msisdn': request.GET.get('msisdn')
        })
    return render_to_response('admin/patient/new_details.html', {
        'form': form
    }, context_instance=RequestContext(request))

@permission_required(LOGIN_PERMISSION, login_url=LOGIN_URL)
def find_patient(request):
    if 'patient_id' in request.GET:
        
        msisdn = request.GET.get('msisdn', '')
        if msisdn:
            msisdn = normalize_msisdn(msisdn)
        
        patients = Patient.objects.filter(
            Q(te_id__icontains=request.GET.get('patient_id','')) |
            Q(active_msisdn__msisdn=msisdn))
            # TODO: add surname to patient model field
        return render_to_response('admin/patient/results.html', {
            'patients': patients,
            'next': request.GET.get('next')
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('admin/patient/find.html', {
            'next': request.GET.get('next')
        }, context_instance=RequestContext(request))

@permission_required(LOGIN_PERMISSION, login_url=LOGIN_URL)
def new_appointment(request):
    return render_to_response('admin/appointment/new.html', {
        'patient': get_object_or_404(Patient, pk=request.GET.get('patient_id'))
    }, context_instance=RequestContext(request))

@permission_required(LOGIN_PERMISSION, login_url=LOGIN_URL)
def new_appointment_details(request):
    return render_to_response('admin/appointment/details.html', {
        # 'date': ''.strptime()
    }, context_instance=RequestContext(request))