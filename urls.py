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


from os import path
from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment this for admin docs:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'', include('general.jquery.urls')),
    (r'^therapyedge/', include('therapyedge.urls')),
    (r'^bookingtool/', include('bookingtool.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', \
                            {'document_root': settings.MEDIA_ROOT}, "static"),
)
