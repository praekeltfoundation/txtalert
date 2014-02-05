# from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404

from piston.handler import BaseHandler
from piston.utils import rc, require_mime, throttle

from txtalert.apps.gateway.models import SendSMS, PleaseCallMe
from txtalert.apps.gateway import gateway, sms_receipt_handler
from txtalert.core.models import Patient, Visit, MSISDN
from txtalert.core.models import PleaseCallMe as CorePleaseCallMe
from txtalert.core.utils import normalize_msisdn
from txtalert.core.forms import RequestCallForm

from django.utils import timezone
from datetime import datetime, timedelta, date
import logging
import iso8601
import json
import re
import pytz

def handle_voicemail_message(message):
    msisdn = r'(?P<msisdn>[0-9]+)'
    time = r'(?P<hour>\d+):(?P<minute>\d+)'
    date = r'(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)'
    sms_patterns = [
        r'Missed call: %s, %s %s' % (msisdn, time, date),
        r'You have \d+ new messages?.\s+The last message from %s was left at %s %s. Please dial 121' % (msisdn, date, time),
    ]

    for pattern in sms_patterns:
        match = re.match(pattern, message)
        if match:
            dictionary = match.groupdict()
            timestamp = datetime(*map(int, [
                dictionary.get(key) for key in [
                    'year', 'month', 'day', 'hour', 'minute'
                ]
            ]))
            return dictionary['msisdn'], timestamp



class SMSHandler(BaseHandler):
    allowed_methods = ('POST', 'GET')
    fields = ('identifier', 'delivery', 'expiry', 'delivery_timestamp',
                'status', 'status_display', 'msisdn')
    model = SendSMS

    @throttle(10, 60)
    def read(self, request, msisdn=None, identifier=None):
        if not request.user.has_perm('gateway.can_view_sms_statistics'):
            return rc.FORBIDDEN

        if all([msisdn, identifier]):
            return get_object_or_404(SendSMS, msisdn=msisdn, user=request.user,
                                        identifier=identifier)
        else:
            return self._read_list(request)

    def _read_list(self, request):
        if 'since' in request.GET:
            # remove timezone info since MySQL is not able to handle that
            # assume input it UTC
            since = iso8601.parse_date(request.GET['since']).replace(
                tzinfo=pytz.UTC)
            return SendSMS.objects.filter(delivery__gte=since, user=request.user)
        else:
            return rc.BAD_REQUEST


    @throttle(10, 60)
    @require_mime('json')
    def create(self, request):
        if not request.user.has_perm('gateway.can_send_sms'):
            return rc.FORBIDDEN

        if request.content_type:
            msisdns = request.data.get('msisdns',[])
            smstext = request.data.get('smstext','')
            if len(smstext) <= 160 and len(msisdns) > 0:
                return gateway.send_sms(request.user, msisdns, (smstext,) * len(msisdns))
        return rc.BAD_REQUEST

    @classmethod
    def status_display(self, instance):
        return instance.get_status_display()


class SMSReceiptHandler(BaseHandler):
    """This is completely handed off to the specified gateway, it should
    specify the sms_receipt_handler, this can be a regular Django view
    responding some type of HttpResponse object"""
    allowed_methods = ('POST',)

    def create(self, request):
        return sms_receipt_handler(request)


class PCMHandler(BaseHandler):
    allowed_methods = ('POST', 'GET')
    fields = ('sms_id', 'sender_msisdn', 'recipient_msisdn', 'created_at')
    model = PleaseCallMe

    @throttle(10, 60)
    def read(self, request):
        """
        Return the list of PleaseCallMe's received since the timestamp specified
        in the `since` parameter.
        """
        if not request.user.has_perm('gateway.can_view_pcm_statistics'):
            return rc.FORBIDDEN

        if 'since' in request.GET:
            # remove timezone info since MySQL is not able to handle that
            # assume input it UTC
            since = iso8601.parse_date(request.GET['since']).replace(
                tzinfo=pytz.UTC)
            return PleaseCallMe.objects.filter(
                user=request.user, created_at__gte=since)
        else:
            return rc.BAD_REQUEST

    def write_sms(self, user, sms_id, sender_msisdn, recipient_msisdn, message):
        if isinstance(message, unicode):
            message = message.encode('unicode_escape')

        if sender_msisdn == '121':
            match = handle_voicemail_message(message)
            if match:
                sender_msisdn, date = match
                message = "Missed call from %s, left at %s." % (sender_msisdn, date)

        # check for duplicate submissions
        if PleaseCallMe.objects.filter(
            sender_msisdn=sender_msisdn,
            message=message,
            created_at__gt=timezone.now() - timedelta(hours=2)).exists():
            resp = rc.DUPLICATE_ENTRY
            resp.content = ''
            resp['Content-Length'] = 0
            return resp

        pcm = PleaseCallMe.objects.create(
            user=user, sms_id=sms_id, sender_msisdn=sender_msisdn,
            recipient_msisdn=recipient_msisdn, message=message)
        resp = rc.CREATED
        resp.content = 'Please Call Me registered'
        resp['Content-Length'] = len(resp.content)
        return resp


    def create(self, request):
        """
        FIXME: This should probably be moved into something more pluggable, it
                shouldn't rely on FrontlineSMS. FrontlineSMS should be one of
                several options

        Receive a please call me message from somewhere, probably FrontlineSMS
        My current FrontlineSMS setup is configured to perform an HTTP request
        triggered by a keyword.

        This is the current URL being requested:

        http://localhost:8000/api/v1/pcm.json? \
                &sender_msisdn=${sender_number} \       # where the PCM came from
                &message=${message_content} \           # the original PCM message
                &sms_id=${sms_id} \                     # the SMSC's ID - mb we can use this to avoid duplicates
                &recipient_msisdn=${recipient_number}   # the number the PCM was called to, perhaps we can use this to identify the clinic

        See http://frontlinesms.ning.com/profiles/blog/show?id=2052630:BlogPost:9729
        for available substitution variables.

        """
        if not request.user.has_perm('gateway.can_place_pcm'):
            return rc.FORBIDDEN

        if ('sms_id' in request.POST
            and 'sender_msisdn' in request.POST
            and 'recipient_msisdn' in request.POST):
            sms_id = request.POST.get('sms_id')
            sender_msisdn = request.POST.get('sender_msisdn')
            recipient_msisdn = request.POST.get('recipient_msisdn')
            message = request.POST.get('message', '')
            return self.write_sms(request.user, sms_id, sender_msisdn,
                                    recipient_msisdn, message)
        else:
            try:
                msg = json.loads(request.body)
                return self.write_sms(request.user, msg['message_id'],
                        msg['from_addr'], msg['to_addr'], msg['content'])
            except Exception, e:
                return rc.BAD_REQUEST

class PatientHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):

        patient_id = request.GET.get('patient_id') or None
        msisdn = request.GET.get('msisdn') or None

        if patient_id and msisdn:
            try:
                normalized_msisdn = normalize_msisdn(msisdn)
                patient = Patient.objects.get(active_msisdn__msisdn=normalized_msisdn,
                                                te_id=patient_id)
                try:
                    visit = patient.next_visit()
                    visit_info = [visit.date.year, visit.date.month, visit.date.day]
                    clinic_name = visit.clinic.name
                except Visit.DoesNotExist:
                    visit = None
                    visit_info = []
                    clinic_name = ''

                visits = patient.visit_set.all()
                attended = visits.filter(status='a').count()
                rescheduled = visits.filter(status='r').count()
                missed = visits.filter(status='m').count()
                total = visits.filter(date__lt=date.today()).count()
                if total:
                    attendance = int(float(attended) / float(total) * 100)
                else:
                    attendance = 0.0

                return {
                    'msisdn': msisdn,
                    'patient_id': patient_id,
                    'name': patient.name,
                    'surname': patient.surname,
                    'next_appointment': visit_info,
                    'visit_id': visit.pk if visit else '',
                    'clinic': clinic_name,
                    'attendance': attendance,
                    'total': total,
                    'attended': attended,
                    'rescheduled': rescheduled,
                    'missed': missed,
                }
            except Patient.DoesNotExist:
                pass
        return {}

class ChangeRequestHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        visit_id = request.POST.get('visit_id')
        visit = get_object_or_404(Visit, pk=visit_id)
        change_requested = request.POST.get('when')
        if change_requested == 'later':
            visit.reschedule_later()
            return {'request': 'later'}
        elif change_requested == 'earlier':
            visit.reschedule_earlier()
            return {'request': 'earlier'}

class CallRequestHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        msisdn = normalize_msisdn(request.POST.get('msisdn'))
        msisdn_record, _ = MSISDN.objects.get_or_create(msisdn=msisdn)
        pcm = CorePleaseCallMe(user=request.user, msisdn=msisdn_record,
                timestamp=timezone.now(), message='Please call me!',
                notes='Call request issued via txtAlert Bookings USSD')
        pcm.save()
        return pcm
