from django.conf.urls.defaults import *
from django.contrib.flatpages.views import flatpage
from txtalert.apps.bookings.bookings_admin import views

urlpatterns = patterns('',
    (r'^$', views.index, {}, 'index'),
    (r'^patient/new/$', views.new_patient, {}, 'new_patient'),
    (r'^patient/new/details/$', views.new_patient_details, {}, 'new_patient_details'),
    (r'^patient/find/$', views.find_patient, {}, 'find_patient'),
    (r'^patient/$', views.view_patient, {}, 'view_patient'),
    (r'^patient/(?P<patient_id>\d+)/$', views.edit_patient, {}, 'edit_patient'),
    (r'^appointment/new/$', views.new_appointment, {}, 'new_appointment'),
    (r'^appointment/details/$', views.new_appointment_details, {}, 'new_appointment_details'),
    (r'^appointment/(?P<visit_id>\d+)/$', views.view_appointment, {}, 'view_appointment'),
    (r'^appointment/(?P<visit_id>\d+)/edit/$', views.change_appointment, {}, 'change_appointment'),
    (r'^appointments/$', views.appointments, {}, 'appointments'),
    (r'^change-requests/$', views.change_requests, {}, 'change_requests'),
    (r'^change-requests/(?P<change_request_id>\d+)/$', views.change_request_details, {}, 'change_request_details'),
    (r'^sign-in/$', 'django.contrib.auth.views.login', { 
            'template_name': 'bookings_admin/signin.html' 
        }, 'signin'),
    (r'^sign-out/$', 'django.contrib.auth.views.logout', {
            'template_name': 'bookings_admin/signout.html'
        }, 'signout'),
)

