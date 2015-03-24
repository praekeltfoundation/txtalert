from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView
from django.conf import settings
from txtalert.core.views import testview

if settings.DEBUG:
    template_name = 'home_qa.html'
else:
    template_name = 'home.html'

urlpatterns = patterns('',
    (r'^$', TemplateView.as_view(template_name=template_name)),
    (r'^test$', testview)
)
