from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView

urlpatterns = patterns('',
    (r'^$', TemplateView.as_view(template_name='widget/index.html')),
    (r'^config\.xml$', TemplateView.as_view(template_name='widget/config.xml')),
    (r'^widget\.html$', TemplateView.as_view(template_name='widget/widget.html')),
)