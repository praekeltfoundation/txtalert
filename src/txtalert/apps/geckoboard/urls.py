from django.conf.urls.defaults import *
from txtalert.apps.geckoboard import views

urlpatterns = patterns('',
    (r'^patient_count/$', views.patient_count),
    (r'^smss_sent/$', views.smss_sent),
    (r'^smss_sent/breakdown/$', views.smss_sent_breakdown),
    (r'^pcms_received/$', views.pcms_received),
    (r'^visit_status/$', views.visit_status),
    (r'^visit_status/(?P<status>[a|m|s|r])/$', views.visit_attendance),
)