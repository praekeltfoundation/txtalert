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


def plist_from_dict(d):
    """Convert a Python dict into a JavaScript property list.
    The order of the items in the returned string is undefined."""
    return ', '.join(['%s: %r' % kv for kv in d.items()])


def args_from_list(l):
    return ', '.join(["'%s'" % i for i in l])



def js_method_call(id, name, *args, **kwargs):
    output = [u"<script type='text/javascript'>",]
    output.append('$(document).ready(function () {')
    output.append("$('#%(id)s').%(method)s(%(args)s, {%(options)s});" % {
        'id': id,
        'method': name,
        'args': args_from_list(args),
        'options': plist_from_dict(kwargs),
    })
    output.append('});');
    output.append('</script>')
    return '\n'.join(output)
