from django.conf.urls.defaults import *
from txtalert.apps.geckoboard import views

urlpatterns = patterns('',
    (r'^patient_count/$', views.patient_count),
)