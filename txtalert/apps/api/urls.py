from django.conf.urls.defaults import *

from txtalert.apps.api import views


# PCM api
urlpatterns = patterns(
    '',
    url(r'^pcm\.json$', views.pcm, {}, 'api-pcm'),
)
