from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

@login_required(login_url='/bookings/signin/')
def index(request):
    return HttpResponse("hi!")

def signin(request):
    return render_to_response('signin.html', locals(), 
                                context_instance=RequestContext(request))