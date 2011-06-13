from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from txtalert.core.models import Visit

@login_required
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
    elif change_requested == 'earlier':
        visit.reschedule_earlier()
    
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
    effective_page_range = [p for p in range(page.number-3,page.number+3) 
                            if (p > 0 and p <= paginator.num_pages)]
    return render_to_response("appointment/upcoming.html", {
        'profile': profile,
        'patient': profile.patient,
        'paginator': paginator,
        'page': page,
        'effective_page_range': effective_page_range
    }, context_instance = RequestContext(request))

def todo(request):
    """Anything that resolves to here still needs to be completed"""
    return HttpResponse("This still needs to be implemented.")
