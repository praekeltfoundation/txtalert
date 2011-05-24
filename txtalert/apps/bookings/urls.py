from django.conf.urls.defaults import *
from txtalert.apps.bookings import views

urlpatterns = patterns('',
    (r'^$', views.index, {}, 'index'),
    (r'^sign-in/$', views.signin, {}, 'signin'),
)

