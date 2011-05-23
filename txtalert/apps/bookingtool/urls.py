from django.conf.urls.defaults import *
from txtalert.apps.bookingtool import views

urlpatterns = patterns('',
    (r'verification\.html', views.verification, {}, 'verification-sms'),
    (r'calendar/risk\.js', views.risk, {}, 'calendar-risk'),
    (r'calendar/suggest\.js', views.suggest, {}, 'calendar-suggest'),
    (r'calendar/(?P<year>\d{4})/(?P<month>\d{1,2})\.html', views.calendar, {}, 'calendar-date'),
    (r'calendar/today.html', views.today, {}, 'calendar-today'),
)
