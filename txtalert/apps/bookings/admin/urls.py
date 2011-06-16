from django.conf.urls.defaults import *
from django.contrib.flatpages.views import flatpage
from txtalert.apps.bookings.admin import views

urlpatterns = patterns('',
    (r'^$', views.index, {}, 'index'),
    (r'^sign-in/$', 'django.contrib.auth.views.login', { 
            'template_name': 'admin/signin.html' 
        }, 'signin'),
    (r'^sign-out/$', 'django.contrib.auth.views.logout', {
            'template_name': 'admin/signout.html'
        }, 'signout'),
)

