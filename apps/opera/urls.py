from django.conf.urls.defaults import *
from opera import views

urlpatterns = patterns('',
    (r'receipt$', views.receipt, {}, 'sms-receipt'),
    (r'receipt/$', views.receipt, {}, 'sms-receipt'),
    )
