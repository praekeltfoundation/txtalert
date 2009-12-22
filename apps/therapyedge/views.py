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


from datetime import date, datetime, timedelta

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.db import connection
from django.contrib.admin.views.decorators import staff_member_required

from general.settings import Setting
from models import MSISDN, Patient, PleaseCallMe
from mobile.sms.models import SMSLog, SMSSendAction
from importing import MSISDN_RE

import reminders, importing


def test(request):
    from xmlrpclib import ServerProxy, Error
    SERVICE_URL = 'https://196.36.218.99/tools/ws/sms/patients/server.php'
    server = ServerProxy(SERVICE_URL)
    data = server.patients_data('patientlist', 0, '', '', 3, '02')
    return HttpResponse(data)

@staff_member_required
def pcm(request):
    """ Registers a new Please Call Me from an MSISDN """
    msisdn = request.GET.get('msisdn', None)
    if msisdn:
        match = MSISDN_RE.match(msisdn)
        if match:
            msisdn = '27' + match.groups()[1]
            msisdn, created = MSISDN.objects.get_or_create(msisdn=msisdn)
            pcm = PleaseCallMe.objects.create(msisdn=msisdn, timestamp=datetime.now())
            return HttpResponse(True)
    return HttpResponse(False)


@staff_member_required
def patient_import(request):
    events = importing.importPatients()

    return render_to_response('admin/therapyedge/import.html', {
        'title': 'Patient Import',
        'user': request.user,
        'events': events,
    })


@staff_member_required
def patient_riskcalc(request):
    for patient in Patient.objects.all():
        if patient.visit_set.count() > 0:
            patient.risk_factor = float(patient.visit_set.filter(status='m').count()) / patient.visit_set.count()
            patient.save()

    return render_to_response('admin/therapyedge/fake_base.html', {
        'title': 'Risk Calculation Complete',
        'user': request.user,
    })
    

@staff_member_required
def visit_import(request):
    events = importing.importVisits()

    return render_to_response('admin/therapyedge/import.html', {
        'title': 'Visit Import',
        'user': request.user,
        'events': events,
    })


@staff_member_required
def action(request, action):
    if action:
        today = datetime.now().date()
        gateway = Setting.objects.get(name='Gateway').value
        
        if action == 'import': importing.importAll()
        elif action == 'send-stats': reminders.send_stats(gateway, today)
        elif action == 'send-all': reminders.all(gateway)
        elif action == 'send-missed': reminders.missed(gateway, today)
        elif action == 'send-attended': reminders.attended(gateway, today)
        elif action == 'send-tomorrow': reminders.tomorrow(gateway, today)
        elif action == 'send-twoweeks': reminders.twoweeks(gateway, today)

    return render_to_response('admin/therapyedge/action.html', {
        'title': 'Actions',
        'user': request.user,
        'action': action,
    })


@staff_member_required
def stats(request):
    end = datetime.now().date()
    start = end - timedelta(days=30)

    month = {}
    for i in range(0, 30):
        mark = start + timedelta(days=i)
        month[mark] = {'date':mark}

    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            DATE(DATE_FORMAT(action.end, '%%Y-%%m-%%d')) AS date,
            SUM(log.count) AS count
        FROM
            (SELECT action_id, COUNT(*) AS count FROM sms_smslog GROUP BY action_id) AS log
            LEFT JOIN
            sms_smssendaction AS action
            ON log.action_id = action.id
        WHERE action.end > %(start)s AND action.end < %(end)s
        GROUP BY date;
    """, {'start': start, 'end': end,})
    messages = dict(cursor.fetchall())
    for day in month.keys(): month[day]['messages'] = messages.get(day, None) or 0

    cursor.execute("""
        SELECT
            date, COUNT(*) AS count
        FROM
            therapyedge_visitevent
            WHERE status = 'a' AND
            date > %(start)s AND date < %(end)s
        GROUP BY date;
    """, {'start': start, 'end': end,})
    attended = dict(cursor.fetchall())
    for day in month.keys(): month[day]['attended'] = attended.get(day, None) or 0

    cursor.execute("""
        SELECT
            date, COUNT(*) AS count
        FROM
            therapyedge_visitevent
            WHERE status = 'm' AND
            date > %(start)s AND date < %(end)s
        GROUP BY date;
    """, {'start': start, 'end': end,})
    missed = dict(cursor.fetchall())
    for day in month.keys(): month[day]['missed'] = missed.get(day, None) or 0


    end = datetime.now().date()
    start = end - timedelta(days=365)

    year = {}
    for i in range(0, 12):
        mark = start + timedelta(days=(i*31))
        mark = date(mark.year, mark.month, 1)
        year[mark] = {'date':mark}

    cursor.execute("""
        SELECT
            DATE(DATE_FORMAT(action.end, '%%Y-%%m-01')) AS date,
            SUM(log.count) AS count
        FROM
            (SELECT action_id, COUNT(*) AS count FROM sms_smslog GROUP BY action_id) AS log
            LEFT JOIN
            sms_smssendaction AS action
            ON log.action_id = action.id
        WHERE action.end > %(start)s AND action.end < %(end)s
        GROUP BY date;
    """, {'start':start, 'end':end})
    messages = dict(cursor.fetchall())
    for m in year.keys(): year[m]['messages'] = messages.get(m, None) or 0

    cursor.execute("""
        SELECT
            DATE(DATE_FORMAT(date, '%%Y-%%m-01')) AS mark,
            COUNT(*) AS count
        FROM
            therapyedge_visitevent
            WHERE status = 'a' AND
            date > %(start)s AND date < %(end)s
        GROUP BY mark;
    """, {'start': start, 'end': end,})
    attended = dict(cursor.fetchall())
    for m in year.keys(): year[m]['attended'] = attended.get(m, None) or 0

    cursor.execute("""
        SELECT
            DATE(DATE_FORMAT(date, '%%Y-%%m-01')) AS mark,
            COUNT(*) AS count
        FROM
            therapyedge_visitevent
            WHERE status = 'm' AND
            date > %(start)s AND date < %(end)s
        GROUP BY mark;
    """, {'start': start, 'end': end,})
    missed = dict(cursor.fetchall())
    for m in year.keys(): year[m]['missed'] = missed.get(m, None) or 0

    month = month.values()
    month.sort(lambda x, y: cmp(x['date'], y['date']))

    year = year.values()
    year.sort(lambda x, y: cmp(x['date'], y['date']))

    risk_profiles = (
        {'name': 'High', 'min':0.8, 'max':1.1},
        {'name': 'Medium', 'min':0.5, 'max':0.8},
        {'name': 'Low', 'min':0.0, 'max':0.5},
    )

    for profile in risk_profiles:
        min, max = profile['min'], profile['max']
        profile['count'] = Patient.objects.filter(risk_profile__gte=min, risk_profile__lt=max).count()
        profile['link'] = '/admin/therapyedge/patient/?risk_profile__gte=%.1f&risk_profile__lt=%.1f' % (min, max)

    return render_to_response('admin/therapyedge/stats.html', {
        'title': 'Statistics',
        'user': request.user,
        'month': month,
        'year': year,
        'risk_profiles': risk_profiles,
    })
