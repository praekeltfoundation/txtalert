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


from django import forms
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from . import js_method_call


class FilteredSelectWidget(forms.Select):
    class Media:
        js = (
            '/media/jquery/js/jquery.js',
            '/media/jquery/js/jquery.filteredselect.js',
        )

    def __init__(self, related_field, attrs=None):
        super(FilteredSelectWidget, self).__init__(attrs)
        self.related_field_query = '#id_' + related_field

    def render(self, name, value, attrs=None):
        output = [super(FilteredSelectWidget, self).render(name, value, attrs),]
        output.append(
            js_method_call(
                attrs['id'],
                'filteredselect',
                self.related_field_query
            )
        )
        return mark_safe(u'\n'.join(output))
