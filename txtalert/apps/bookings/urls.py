from django.conf.urls.defaults import *
from txtalert.apps.bookings import views

urlpatterns = patterns('',
    (r'^$', views.index, {}, 'index'),
    (r'^todo/.*', views.todo, {}, 'todo'),
    (r'^appointment/change/(?P<visit_id>\d+)/$', views.appointment_change, {}, 'appointment_change'),
    (r'^appointment/upcoming/$', views.appointment_upcoming, {}, 'appointment_upcoming'),
    (r'^sign-in/$', 'django.contrib.auth.views.login', { 
            'template_name': 'signin.html' 
        }, 'signin'),
    (r'^sign-out/$', 'django.contrib.auth.views.logout', {
            'template_name': 'signout.html'
        }, 'signout'),
)

