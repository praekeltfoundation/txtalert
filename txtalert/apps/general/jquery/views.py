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


from django.utils import simplejson as json
from django.http import HttpResponse
from django.db.models import get_model, Q


def autocomplete(request, app, model, field):
    model = get_model(app, model)
    limit = request.REQUEST.get('limit', 10)
    value = request.REQUEST.get('input_content', '')
    # Setup and execute the query
    terms = [field + '__istartswith',]
    qargs = dict([(str(t), value) for t in terms])
    result = model.objects.filter(Q(**qargs)).values('pk', field)[:limit]
    # Orientate the data so that it makes sense to james
    result = [{'text':r[field], 'json':{'pk':r['pk']}} for r in result]
    return HttpResponse(json.dumps(result), content_type='application/json')
