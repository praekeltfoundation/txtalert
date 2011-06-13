from django.conf.urls.defaults import *
from django.views.generic.base import TemplateView
from txtalert.apps.bookings import views

urlpatterns = patterns('',
    (r'^$', views.index, {}, 'index'),
    (r'^todo/.*', views.todo, {}, 'todo'),
    (r'^appointment/change/(?P<visit_id>\d+)/$', views.appointment_change, {}, 'appointment_change'),
    (r'^appointment/upcoming/$', views.appointment_upcoming, {}, 'appointment_upcoming'),
    (r'^appointment/history/$', views.appointment_history, {}, 'appointment_history'),
    (r'^attendance/barometer/$', views.attendance_barometer, {}, 'attendance_barometer'),
    (r'^request-call/$', views.request_call, {}, 'request_call'),
    (r'^terms-of-service/$', TemplateView.as_view(template_name='terms_of_service.html'), {}, 'terms_of_service'),
    (r'^privacy/$', TemplateView.as_view(template_name='privacy.html'), {}, 'privacy'),
    (r'^sign-in/$', 'django.contrib.auth.views.login', { 
            'template_name': 'signin.html' 
        }, 'signin'),
    (r'^sign-out/$', 'django.contrib.auth.views.logout', {
            'template_name': 'signout.html'
        }, 'signout'),
)

