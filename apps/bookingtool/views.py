import sys, traceback
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.simplejson import dumps
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from txtalert.core.models import Visit
from cal import *
from datetime import date, datetime, timedelta
from bookingtool.models import BookingPatient
from gateway import gateway
import logging


def suggest(request):
    if 'patient_id' in request.GET:
        patient_id = request.GET['patient_id']
        # patient id == -1 for patients that haven't been created yet, unknown id
        if patient_id == '-1':
            # default to monthly for now
            treatment_cycle = int(request.GET.get('treatment_cycle',1))
            suggestion = datetime.now() + timedelta(treatment_cycle * 365 / 12)
        else:
            bp = BookingPatient.objects.get(pk=request.GET['patient_id'])
            treatment_cycle = int(request.GET.get('treatment_cycle',None) or bp.treatment_cycle)
            if Visit.objects.filter(patient=bp).count():
                last_visit = Visit.objects.filter(patient=bp).latest('date')
                # take last visit & calculate treatment_cycle amount of months forward
                suggestion = last_visit.date + timedelta(treatment_cycle * 365 / 12)
            else:
                suggestion = datetime.now() + timedelta(treatment_cycle * 365 / 12)
        return HttpResponse(dumps({
            'suggestion': "%s-%s-%s" % (suggestion.year, suggestion.month, suggestion.day)
        }), content_type='text/json')
    else:
        raise Http404

def risk(request):
    if 'date' in request.GET:
        year, month, day = map(int, request.GET.get('date', None).split('-'))
        level = risk_on_date(date(year, month, day))
        return HttpResponse(dumps({'risk': level}))
    else:
        raise Http404

def today(request):
    today = datetime.now()
    return HttpResponseRedirect(reverse('calendar-date', kwargs={
        'month': today.month,
        'year': today.year
    }))

def calendar(request, year, month):
    year, month = int(year), int(month)
    visits = Visit.objects.order_by('date').filter(date__year=year, \
                                                    date__month=month)
    
    # render the calendar with events for the given year & month
    calendar = mark_safe(RiskCalendar(visits).formatmonth(year, month))
    
    now = datetime.now().date()
    
    # shamelessly pulled from Django's date_based.archive_month
    # first day of this month, use it to calculate previous & next months
    first_day = date(year, month, day=1)
    
    if first_day.month == 1:
        previous_month = first_day.replace(year=first_day.year-1,month=12)
    else:
        previous_month = first_day.replace(month=first_day.month-1)
    
    if first_day.month == 12:
        next_month = first_day.replace(year=first_day.year + 1, month=1)
    else:
        next_month = first_day.replace(month=first_day.month + 1)

    return render_to_response('calendar.html', locals())

def verification(request):
    msisdn = request.POST.get('msisdn',None)
    gateway.send_sms([msisdn], ['Welcome to TxtAlert!'])
    response = "<span class='success'>SMS has been sent to %(msisdn)s</span>"
    return HttpResponse(response)
