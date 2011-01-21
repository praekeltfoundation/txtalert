# Copyright (c) 2009, Jurie-Jan Botha
#
# This file is part of the 'settings' Django application.
#
# 'settings' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# 'settings' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with the 'settings' application. If not, see
# <http://www.gnu.org/licenses/>.


from django.contrib import admin

from models import *


class SettingAdmin(admin.ModelAdmin):
    fields = ('name', 'type', 'int_value', 'text_value', 'object_type', 'object_id')

    class Media:
        js = ('/scriptaculous/media/js/prototype.js',)


admin.site.register(Setting, SettingAdmin)
