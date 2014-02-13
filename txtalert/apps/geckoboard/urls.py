from django.conf.urls import patterns, url, include
from txtalert.apps.geckoboard import views

urlpatterns = patterns('',
    (r'^total_patient_count/$', views.total_patient_count),
    (r'^total_patient_distribution/$', views.total_patient_distribution),
    (r'^patient_count/$', views.patient_count),
    (r'^smss_sent/$', views.smss_sent),
    (r'^smss_sent/breakdown/$', views.smss_sent_breakdown),
    (r'^pcms_received/$', views.pcms_received),
    (r'^visit_status/$', views.visit_status),
    (r'^visit_status/(?P<status>[a|m|s|r])/$', views.visit_attendance),
)