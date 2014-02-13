#  This file is part of TxtAlert.
#
#  TxtALert is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TxtAlert is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with TxtAlert.  If not, see <http://www.gnu.org/licenses/>.


import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib import admin
admin.autodiscover()

from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse

from txtalert.core import clinic_admin


def health(request):
    return HttpResponse('')

# web site
urlpatterns = patterns(
    '',
    (r'', include('txtalert.apps.general.jquery.urls')),
    (r'', include('txtalert.core.urls')),
    (r'^therapyedge/', include('txtalert.apps.therapyedge.urls')),
    (r'^bookings/',
        include('txtalert.apps.bookings.urls', namespace='bookings')),
    (r'^widget/', include('txtalert.apps.widget.urls')),
    (r'^geckoboard/', include('txtalert.apps.geckoboard.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^clinic/admin/', include(clinic_admin.site.urls)),
)

# auto complete, done here manually because I need to add the
# login_required decorator.
urlpatterns += patterns(
    '',
    url(r'^(?P<autocomplete>[-\w]+)/$',
        login_required(autocomplete_light.views.AutocompleteView.as_view()),
        name='autocomplete_light_autocomplete'),
    url(r'^$',
        login_required(autocomplete_light.views.RegistryView.as_view()),
        name='autocomplete_light_registry'),
)

# web API
urlpatterns += patterns(
    '',
    (r'^api/v1/', include('txtalert.apps.api.urls')),
)

# HAProxy health check
urlpatterns += patterns(
    '',
    url(r'^health/$', health, name="health")
)

# statics
urlpatterns += staticfiles_urlpatterns()
