from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils.simplejson import dumps
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe

from therapyedge.models import Visit
from cal import *
from datetime import date, datetime

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
    return calendar(request, today.year, today.month)

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