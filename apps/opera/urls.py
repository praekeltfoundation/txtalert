from django.conf.urls.defaults import *
from opera import views

# URL patterns for SMSs
urlpatterns = patterns('',
    # Intentional url without or without trailing slash as Opera seems to
    # chop it off the URL posted in Dragon's General Configuration area.
    (r'^receipt/?$', views.receipt, {}, 'sms-receipt'),
    (r'^statistics\.(?P<format>json|xml)$', views.send_sms_statistics, {}, 'sms-statistics'),
    (r'^send\.(?P<format>json|xml)$', views.send_sms, {}, 'sms-send'),
)

# URL patterns for PCMs
urlpatterns += patterns('', 
    (r'^pcm/?$', views.pcm, {}, 'sms-pcm'),
    (r'^pcm/statistics\.(?P<format>json|xml)$', views.pcm_statistics, {}, 'sms-pcm-statistics'),
)
