from django.conf.urls.defaults import *
from django.contrib.flatpages.views import flatpage
from txtalert.apps.bookings import views

urlpatterns = patterns('',
    (r'^$', views.index, {}, 'index'),
    (r'^admin/', include('txtalert.apps.bookings.bookings_admin.urls', namespace='admin')),
    (r'^todo/.*', views.todo, {}, 'todo'),
    (r'^appointment/change/(?P<visit_id>\d+)/$', views.appointment_change, {}, 'appointment_change'),
    (r'^appointment/upcoming/$', views.appointment_upcoming, {}, 'appointment_upcoming'),
    (r'^appointment/history/$', views.appointment_history, {}, 'appointment_history'),
    (r'^attendance/barometer/$', views.attendance_barometer, {}, 'attendance_barometer'),
    (r'^request-call/$', views.request_call, {}, 'request_call'),
    (r'^404/$', views.not_found, {}, 'not_found'),
    (r'^500/$', views.server_error, {}, 'server_error'),
    (r'^sign-in/$', 'django.contrib.auth.views.login', { 
            'template_name': 'signin.html' 
        }, 'signin'),
    (r'^sign-out/$', 'django.contrib.auth.views.logout', {
            'template_name': 'signout.html'
        }, 'signout'),
)

