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
from django.contrib.auth.models import Group

from txtalert.apps.general.settings.models import Setting
from txtalert.apps.gateway.models import SendSMS
from txtalert.core.models import Visit
import logging

logger = logging.getLogger("reminders")


REMINDERS_EMAIL_TEXT = \
"""
%(total)s TXTAlert Messages Sent on %(date)s
Attened Yesterday: %(attended)s
Missed Yesterday: %(missed)s (%(missed_percentage).1f%%)
Pending Tomorrow: %(tomorrow)s
Pending in 2 weeks: %(two_weeks)s
"""

REMINDERS_SMS_TEXT = \
"""
TXTAlert %(total)s Messages Sent:
Attended Yesterday - %(attended)s
Missed Yesterday - %(missed)s (%(missed_percentage).1f%%)
Pending Tomorrow - %(tomorrow)s
Pending in 2 weeks- %(two_weeks)s
"""


from itertools import groupby
def group_by_language(patients):
    grouper = lambda patient: patient.language
    return dict(
        [(language, list(patients_per_language)) for \
                language, patients_per_language in groupby(patients, grouper)]
    )

def send_stats(gateway, group_names, today):
    for group in Group.objects.filter(name__in=group_names):
        send_stats_for_group(gateway, today, group)

def send_stats_for_group(gateway, today, group):
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    twoweeks = today + timedelta(weeks=2)
    
    users = group.user_set.all()
    visits = Visit.objects.filter(patient__opted_in=True, 
                                    patient__owner__in=users)
    
    # get stats for today's bulk of SMSs sent
    tomorrow_count = visits.filter(date__exact=tomorrow).count()
    twoweeks_count = visits.filter(date__exact=twoweeks).count()
    attended_count = visits.filter(status__exact='a', date__exact=yesterday).count()
    missed_count = visits.filter(status__exact='m', date__exact=yesterday).count()
    
    yesterday_count = missed_count + attended_count
    if yesterday_count == 0: missed_percentage = 0
    else: missed_percentage = missed_count * (100.0 / yesterday_count)
    
    # for every SMS sent we have an entry of SendSMS
    total_count = SendSMS.objects.filter(delivery__gte=today, user__in=users).count()
    
    # send email with stats
    emails = Setting.objects.get(name='Stats Emails').value.split('\r\n')
    message = REMINDERS_EMAIL_TEXT % {
        'total': total_count, 
        'date': today, 
        'attended': attended_count,
        'missed': missed_count, 
        'missed_percentage': missed_percentage,
        'tomorrow': tomorrow_count, 
        'two_weeks': twoweeks_count
    }
    logger.info('Sending stat emails to: %s' % ', '.join(emails))
    logger.debug(message)
    mail.send_mail('[TxtAlert] Messages Sent Report', message, settings.SERVER_EMAIL, emails, fail_silently=True)
    
    # send sms with stats
    msisdns = Setting.objects.get(name='Stats MSISDNs').value.split('\r\n')
    message = REMINDERS_SMS_TEXT % {
        'total': total_count, 
        'attended': attended_count,
        'missed': missed_count, 
        'missed_percentage': missed_percentage,
        'tomorrow': tomorrow_count, 
        'two_weeks': twoweeks_count,
    }
    logger.info('Sending stat SMSs to: %s' % ', '.join(msisdns))
    logger.debug(message)
    # FIXME: I'm always using the first user in the list as the one sending the
    #        stats SMS for this group 
    gateway.send_sms(users[0], msisdns, [message] * len(msisdns))
    


def send_messages(gateway, user, message_key, patients, message_formatter=lambda x: x):
    send_sms_per_language = {}
    for language, patients in group_by_language(patients).items():
        # We only can send messages to patients with an active msisdn
        patients = filter(lambda p:p.active_msisdn, patients)
        message = message_formatter(getattr(language, message_key))
        # we make a set out of it to avoid having duplicate MSISDNs, this can
        # happen if a patient has two different visits on the same day
        msisdns = set([patient.active_msisdn.msisdn for patient in patients])
        send_sms_per_language[language] = gateway.send_sms(
            user,
            msisdns, 
            [message] * len(msisdns)
        )
    return send_sms_per_language

def tomorrow(gateway, user, visits, today):
    # send reminders for patients due tomorrow
    tomorrow = today + timedelta(days=1)
    visits_tomorrow = visits.filter(date__exact=tomorrow).select_related()
    return send_messages(
        gateway,
        user,
        message_key='tomorrow_message',
        patients=[visit.patient for visit in visits_tomorrow]
    )


def two_weeks(gateway, user, visits, today):
    # send reminders for patients due in two weeks
    twoweeks = today + timedelta(weeks=2)
    visits_in_two_weeks = visits.filter(date__exact=twoweeks).select_related()
    return send_messages(
        gateway,
        user,
        message_key='twoweeks_message',
        patients=[visit.patient for visit in visits_in_two_weeks],
        message_formatter=lambda msg: msg % {'date': twoweeks.strftime('%A %d %b')}
    )


def attended(gateway, user, visits, today):
    # send reminders to patients who attended their visits
    yesterday = today - timedelta(days=1)
    attended_yesterday = visits.filter(status__exact='a', \
                                        date__exact=yesterday).select_related()
    return send_messages(
        gateway,
        user,
        message_key='attended_message',
        patients=[visit.patient for visit in attended_yesterday]
    )


def missed(gateway, user, visits, today):
    # send reminders to patients who missed their visits
    yesterday = today - timedelta(days=1)
    missed_yesterday = visits.filter(status__exact='m', \
                                        date__exact=yesterday).select_related()
    return send_messages(
        gateway,
        user,
        message_key='missed_message',
        patients=[visit.patient for visit in missed_yesterday]
    )


def all(gateway, group_names):
    groups = Group.objects.filter(name__in=group_names)
    for group in groups:
        for user in group.user_set.all():
            visits = Visit.objects.filter(patient__opted_in=True,
                                            clinic__user=user)
            today = datetime.now().date()
            logger.debug('Sending reminders for %s: tomorrow' % user)
            tomorrow(gateway, user, visits, today)
            logger.debug('Sending reminders for %s: two weeks' % user)
            two_weeks(gateway, user, visits, today)
            logger.debug('Sending reminders for %s: attended yesterday' % user)
            attended(gateway, user, visits, today)
            logger.debug('Sending reminders for %s: missed yesterday' % user)
            missed(gateway, user, visits, today)
