from django.conf.urls.defaults import *
from django.views.generic.base import TemplateView
from django.conf import settings

if settings.DEBUG:
    template_name = 'qa_home.html'
else:
    template_name = 'home.html'

urlpatterns = patterns('',
    (r'^$', TemplateView.as_view(template_name=template_name)),
)
