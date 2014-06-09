from django.conf.urls import patterns, url

from txtalert.apps.api import views


# PCM api
urlpatterns = patterns(
    '',
    url(r'^pcm\.json$', views.pcm, {}, 'api-pcm'),
    url(r'^events\.json$', views.events, {}, 'api-events'),
)
