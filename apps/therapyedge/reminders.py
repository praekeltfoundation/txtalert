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


from datetime import datetime, timedelta

from django.conf import settings
from django.core import mail

from general.settings.models import Setting
from mobile.sms.models import SMSSendAction
from models import Visit


REMINDERS_EMAIL_TEXT = \
"""
%s TXTAlert Messages Sent on %s
Attened Yesterday: %s
Missed Yesterday: %s (%.1f%%)
Pending Tomorrow: %s
Pending in 2 weeks: %s
"""

REMINDERS_SMS_TEXT = \
"""
TXTAlert %s Messages Sent:
Attended Yesterday - %s
Missed Yesterday - %s (%.1f%%)
Pending Tomorrow - %s
Pending in 2 weeks- %s
"""


def send_stats(gateway, today):
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    twoweeks = today + timedelta(weeks=2)

    visits = Visit.objects.filter(patient__opted_in=True)
    visitevents = VisitEvent.objects.filter(visit__patient__opted_in=True)
    
    tomorrow_count = visits.filter(date__exact=tomorrow).count()
    twoweeks_count = visits.filter(date__exact=twoweeks).count()
    attended_count = visitevents.filter(status__exact='a', date__exact=yesterday).count()
    missed_count = visitevents.filter(status__exact='m', date__exact=yesterday).count()
    yesterday_count = missed_count + attended_count
    if yesterday_count == 0: missed_percentage = 0
    else: missed_percentage = missed_count * (100.0 / yesterday_count)
    total_count = 0
    for action in SMSSendAction.objects.filter(start__gt=today):
        total_count += action.smslogs.count()

    # send email with stats
    emails = Setting.objects.get(name='Stats Emails').value.split('\n')
    message = REMINDERS_EMAIL_TEXT % (
        total_count, today, attended_count,
        missed_count, missed_percentage,
        tomorrow_count, twoweeks_count
    )
    mail.send_mail('[TxtAlert] Messages Sent Report', message, settings.SERVER_EMAIL, emails, fail_silently=True)

    # send sms with stats
    msisdns = Setting.objects.get(name='Stats MSISDNs').value.split('\n')
    message = REMINDERS_SMS_TEXT % (
        total_count, attended_count,
        missed_count, missed_percentage,
        tomorrow_count, twoweeks_count,
    )
    gateway.sendSMS(msisdns, message)
    

def send(gateway, message, *args, **kwargs):
    if kwargs.has_key('visits'):
        msisdns = [v.patient.active_msisdn.msisdn for v in kwargs['visits']]
    elif kwargs.has_key('events'):
        msisdns = [e.visit.patient.active_msisdns.msisdn for e in kwargs['events']]
    if len(msisdns) > 0:
        action = gateway.sendSMS(msisdns, message)
        return action.smslogs.count()
    else:
        return 0


def tomorrow(gateway, visits, today):
    # send reminders for patients due tomorrow
    tomorrow = today + timedelta(days=1)
    count = send(
        gateway,
        Setting.objects.get(name='Tomorrow Visit Reminder').value,
        visits=visits.filter(date__exact=tomorrow).select_related(),
    )
    return count


def two_weeks(gateway, visits, today):
    # send reminders for patients due in two weeks
    twoweeks = today + timedelta(weeks=2)
    count = send(
        gateway,
        (Setting.objects.get(name='Two Weeks Visit Reminder').value % {'date':twoweeks.strftime('%A %d %b')}),
        visits=visits.filter(date__exact=twoweeks).select_related(),
    )
    return count


def attended(gateway, visitevents, today):
    # send reminders to patients who attended their visits
    yesterday = today - timedelta(days=1)
    count = send(
        gateway,
        Setting.objects.get(name='Attended Visit Message').value,
        events=visitevents.filter(status__exact='a', date__exact=yesterday),
    )
    return count
    

def missed(gateway, visitevents, today):
    # send reminders to patients who missed their visits
    yesterday = today - timedelta(days=1)
    count = send(
        gateway,
        Setting.objects.get(name='Missed Visit Message').value,
        events=visitevents.filter(status__exact='m', date__exact=yesterday),
    )
    return count


def all(gateway):
    visits = Visit.objects.filter(patient__opted_in=True)
    visitevents = VisitEvent.objects.filter(visit__patient__opted_in=True)
    today = datetime.now().date()
    tomorrow(gateway, visits, today)
    two_weeks(gateway, visits, today)
    attended(gateway, visitevents, today)
    missed(gateway, visitevents, today)
