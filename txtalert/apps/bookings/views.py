from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

LOGIN_URL = '/bookings/sign-in/'

@login_required(login_url=LOGIN_URL)
def index(request):
    return HttpResponse("hi!")

