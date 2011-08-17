from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
import logging
from txtalert.core.models import Visit, PleaseCallMe, MSISDN, AuthProfile, Patient
from txtalert.core.forms import RequestCallForm
from txtalert.core.utils import normalize_msisdn
from datetime import date, datetime
from functools import wraps

def effective_page_range_for(page,paginator,delta=3):
    return [p for p in range(page.number-delta,page.number+delta+1) 
                if (p > 0 and p <= paginator.num_pages)]

def auth_profile_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except AuthProfile.DoesNotExist:
            return render_to_response('auth_profile_error.html', {
            }, context_instance = RequestContext(request))
    return wrapper

@login_required
@auth_profile_required
def index(request):
    profile = request.user.get_profile()
    return render_to_response("index.html", {
        'profile': profile,
        'patient': profile.patient,
    }, context_instance = RequestContext(request))

@login_required
def appointment_change(request, visit_id):
    profile = request.user.get_profile()
    visit = get_object_or_404(Visit, pk=visit_id)
    change_requested = request.POST.get('when')
    if change_requested == 'later':
        visit.reschedule_later()
        messages.add_message(request, messages.INFO, 
            "Your request to change the appointment has been sent to " \
            "the clinic. You will be notified as soon as possible.")
    elif change_requested == 'earlier':
        visit.reschedule_earlier()
        messages.add_message(request, messages.INFO, 
            "Your request to change the appointment has been sent to " \
            "the clinic. You will be notified as soon as possible.")
    
    return render_to_response("appointment/change.html", {
        'profile': profile,
        'patient': profile.patient,
        'visit': visit,
        'change_requested': change_requested,
    }, context_instance = RequestContext(request))

@login_required
def appointment_upcoming(request):
    profile = request.user.get_profile()
    patient = profile.patient
    paginator = Paginator(patient.visit_set.upcoming(), 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response("appointment/upcoming.html", {
        'profile': profile,
        'patient': patient,
        'paginator': paginator,
        'page': page,
        'effective_page_range': effective_page_range_for(page, paginator)
    }, context_instance = RequestContext(request))

@login_required
def appointment_history(request):
    profile = request.user.get_profile()
    patient = profile.patient
    paginator = Paginator(patient.visit_set.past().order_by('-date'), 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response("appointment/history.html", {
        'profile': profile,
        'patient': profile.patient,
        'paginator': paginator,
        'page': page,
        'effective_page_range': effective_page_range_for(page, paginator)
    }, context_instance=RequestContext(request))
    
@login_required
def attendance_barometer(request):
    profile = request.user.get_profile()
    patient = profile.patient
    visits = patient.visit_set.all()
    attended = visits.filter(status='a').count()
    missed = visits.filter(status='m').count()
    total = visits.filter(date__lt=date.today()).count()
    if total:
        attendance = int(float(attended) / float(total) * 100)
    else:
        attendance = 0.0
    return render_to_response("attendance_barometer.html", {
        'profile': profile,
        'patient': patient,
        'attendance': attendance,
        'attended': attended,
        'missed': missed,
        'total': total
    }, context_instance=RequestContext(request))

def request_call(request):
    if request.POST:
        form = RequestCallForm(request.POST)
        if form.is_valid():
            clinic = form.cleaned_data['clinic']
            # normalize
            msisdn = normalize_msisdn(form.cleaned_data['msisdn'])
            # orm object
            msisdn_record, _ = MSISDN.objects.get_or_create(msisdn=msisdn)
            pcm = PleaseCallMe(user=clinic.user, clinic=clinic, 
                msisdn=msisdn_record, timestamp=datetime.now(), 
                message='Please call me!', notes='Call request issued via txtAlert Bookings')
            pcm.save()
            messages.add_message(request, messages.INFO, 
                        'Your call request has been registered. '\
                        'The clinic will call you back as soon as possible.')
            return HttpResponseRedirect(reverse('bookings:request_call'))
    else:
        form = RequestCallForm(initial={
            'msisdn': '' if request.user.is_anonymous() else request.user.username
        })
    
    if request.user.is_anonymous():
        profile = patient = None
    else:
        profile = request.user.get_profile()
        patient = profile.patient
    
    return render_to_response('request_call.html', {
        'profile': profile,
        'patient': patient,
        'form': form,
    }, context_instance=RequestContext(request))

def widget_landing(request):
    if 'patient_id' in request.GET \
        and 'msisdn' in request.GET:
        
        try:
            msisdn = normalize_msisdn(request.GET.get('msisdn'))
            patient_id = request.GET.get('patient_id')
            patient = Patient.objects.get(active_msisdn__msisdn=msisdn,
                                            te_id=patient_id)
            try:
                visit = patient.next_visit()
            except Visit.DoesNotExist:
                visit = None
            
            visits = patient.visit_set.all()
            
            context = {
                'msisdn': msisdn,
                'patient_id': patient_id,
                'patient': patient,
                'name': patient.name,
                'surname': patient.surname,
                'next_appointment': visit.date if visit else '',
                'visit_id': visit.pk if visit else '',
                'clinic': visit.clinic.name if visit else '',
                'attendance': int((1.0 - patient.risk_profile) * 100),
                'total': visits.count(),
                'attended': visits.filter(status='a').count(),
                'rescheduled': visits.filter(status='r').count(),
                'missed': visits.filter(status='m').count(),
            }
        except Patient.DoesNotExist:
            context = {
                'patient_id': patient_id,
                'msisdn': msisdn,
            }
    else:
        context = {
            'patient_id': request.GET.get('patient_id', ''),
            'msisdn': request.GET.get('msisdn', ''),
        }
    print context
    return render_to_response('widget_landing.html', context, 
        context_instance=RequestContext(request))

def todo(request):
    """Anything that resolves to here still needs to be completed"""
    return HttpResponse("This still needs to be implemented.")

def not_found(request):
    """test 404 template rendering"""
    raise Http404

def server_error(request):
    """test 500 template rendering"""
    raise Exception, '500 testing'