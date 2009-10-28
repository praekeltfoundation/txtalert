from django.conf.urls.defaults import *
from opera import views

urlpatterns = patterns('',
    # Intentional url without trailing slash as Opera seems to chop it off
    # the URL posted in Dragon's General Configuration area.
    (r'receipt$', views.receipt, {}, 'sms-receipt'), 
    (r'receipt/$', views.receipt, {}, 'sms-receipt'),
    (r'statistics\.(?P<format>json|xml|python|yaml)$', views.statistics, {}, 'sms-api'),
)
