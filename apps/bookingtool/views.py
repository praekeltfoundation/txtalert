from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils.simplejson import dumps
from therapyedge.models import Visit
from datetime import date

def availability_on_date(_date):
    visit_count = Visit.objects.filter(date__exact=_date).count()
    for level, check in settings.BOOKING_TOOL_AVAILABILITY_RANGES.items():
        if check(visit_count):
            return level


def availability(request):
    if 'date' in request.GET:
        year, month, day = map(int, request.GET.get('date', None).split('-'))
        level = availability_on_date(date(year, month, day))
        if level:
            return HttpResponse(dumps({'risk': level}))
        else:
            return HttpResponse(dumps({'risk': 'unknown'}))
    else:
        raise Http404