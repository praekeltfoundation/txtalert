from django.conf.urls.defaults import *
from django.contrib.flatpages.views import flatpage
from txtalert.apps.bookings.admin import views

urlpatterns = patterns('',
    (r'^$', views.index, {}, 'index'),
    (r'^patient/new/$', views.new_patient, {}, 'new_patient'),
    (r'^patient/details/$', views.new_patient_details, {}, 'new_patient_details'),
    (r'^patient/find/$', views.find_patient, {}, 'find_patient'),
    (r'^appointment/new/$', views.new_appointment, {}, 'new_appointment'),
    (r'^appointment/details/$', views.new_appointment_details, {}, 'new_appointment_details'),
    (r'^appointment/(?P<visit_id>\d+)/$', views.view_appointment, {}, 'view_appointment'),
    (r'^appointment/(?P<visit_id>\d+)/edit/$', views.change_appointment, {}, 'change_appointment'),
    (r'^appointments/$', views.appointments, {}, 'appointments'),
    (r'^sign-in/$', 'django.contrib.auth.views.login', { 
            'template_name': 'admin/signin.html' 
        }, 'signin'),
    (r'^sign-out/$', 'django.contrib.auth.views.logout', {
            'template_name': 'admin/signout.html'
        }, 'signout'),
)

