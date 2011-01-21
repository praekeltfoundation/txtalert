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
from django.utils.encoding import force_unicode
from django.core.urlresolvers import reverse
from django.conf import settings
from . import plist_from_dict


class AutoCompleteWidget(forms.Widget):
    class Media:
        js = (
            '%sjquery/js/jquery.js' % settings.MEDIA_URL,
            '%sjquery/js/jquery.james.min.js' % settings.MEDIA_URL,
        )
        css = {'all':('%sjquery/css/autocomplete.css' % settings.MEDIA_URL,),}

    def __init__(self, model, field, limit=10, options={}, attrs=None):
        super(AutoCompleteWidget, self).__init__(attrs)
        self.model, self.limit = model, limit
        self.options = {'method':'post'}
        self.options.update(options)
        meta =  model._meta
        self.url = '/jquery/autocomplete/%s/%s/%s/' % (\
            meta.app_label, meta.module_name, field
        )

    def render(self, name, value, attrs=None):
        if value is None: value = ''
        widget_attrs = self.build_attrs(attrs)
        hidden_attrs = {'id':attrs['id'], 'name':name}
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            widget_attrs['value'] = force_unicode(self.model.objects.get(pk=value))
            hidden_attrs['value'] = force_unicode(value)
        widget_attrs['id'] = 'widget_' + attrs['id']
        return mark_safe(u'''
            <div class="autocomplete">
            <input type="text"%(widget_attrs)s />
            <input type="hidden"%(hidden_attrs)s />
            <script type="text/javascript">
                $('#%(widget_id)s').james('%(url)s', {%(options)s,
                    params: 'limit=%(limit)s',
                    onSelect: function(data, json) {
                        $('#%(hidden_id)s').val(json.pk);
                        return data;
                    }
                });
            </script>
            </div>
        ''' % {
            'widget_attrs':flatatt(widget_attrs),
            'hidden_attrs':flatatt(hidden_attrs),
            'widget_id':widget_attrs['id'],
            'hidden_id':hidden_attrs['id'],
            'url':self.url, 'options': plist_from_dict(self.options),
            'limit':self.limit,
        })
