import sys, traceback
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.simplejson import dumps
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from therapyedge.models import Visit
from mobile.sms.models import OperaGateway
from cal import *
from datetime import date, datetime, timedelta
from bookingtool.models import BookingPatient


def suggest(request):
    if 'patient_id' in request.GET:
        bp = BookingPatient.objects.get(pk=request.GET['patient_id'])
        last_visit = bp.visits.latest('date')
        # take last visit & calculate treatment_cycle amount of months forward
        suggestion = last_visit.date + timedelta(bp.treatment_cycle * 365 / 12)
        return HttpResponse(dumps({
            'suggestion': "%s-%s-%s" % (suggestion.year, suggestion.month, suggestion.day)
        }))
    else:
        raise Http404

def risk(request):
    if 'date' in request.GET:
        year, month, day = map(int, request.GET.get('date', None).split('-'))
        level = risk_on_date(date(year, month, day))
        if level:
            return HttpResponse(dumps({'risk': level}))
        else:
            return HttpResponse(dumps({'risk': 'unknown'}))
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
    try:
        msisdn = request.POST.get('msisdn',None)
        gateway = OperaGateway.objects.all()[0]
        gateway.sendSMS([msisdn], 'Welcome to TxtAlert!')
        response = "<span class='success'>SMS has been sent to %(msisdn)s</span>"
    except Exception, e:
        print "Exception in sendSMS code:"
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        response = "<span class='fail'>Failed sending SMS verification to %(msisdn)s</span>"
    return HttpResponse(response % {'msisdn': request.POST.get('msisdn', 'unknown')})
