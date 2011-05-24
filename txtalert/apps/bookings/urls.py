from django.conf.urls.defaults import *
from txtalert.apps.bookings import views

urlpatterns = patterns('',
    (r'^$', views.index, {}, 'index'),
    (r'^sign-in/$', 'django.contrib.auth.views.login', { 
            'template_name': 'signin.html' 
        }, 'signin'),
)

