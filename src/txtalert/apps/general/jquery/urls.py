# Copyright (c) 2009, Jurie-Jan Botha
#
# This file is part of the 'jquery' Django application.
#
# 'jquery' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# 'jquery' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with the 'jquery' application. If not, see
# <http://www.gnu.org/licenses/>.


from os import path
from django.conf.urls.defaults import *
from views import autocomplete

current_path =  path.abspath(path.dirname(__file__))

urlpatterns = patterns('',
    (r'^media/jquery/(?P<path>.*)$', 'django.views.static.serve', {'document_root':current_path + '/media'}),
    (r'^jquery/autocomplete/(?P<app>\w+)/(?P<model>\w+)/(?P<field>\w+)/$', autocomplete),
)
