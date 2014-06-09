from datetime import timedelta
from functools import wraps
import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from txtalert.apps.gateway.models import PleaseCallMe, SendSMS


def expect_json(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if 'application/json' in request.META.get('CONTENT_TYPE', ''):
            request.json = json.load(request)
        else:
            request.json = None
        return func(request, *args, **kwargs)

    return wrapper


@csrf_exempt
@expect_json
def pcm(request):

    user = User.objects.get(username=request.GET['username'])

    msg = request.json
    if msg is not None:
        message_id = msg.get('message_id')
        from_addr = msg.get('from_addr')
        to_addr = msg.get('to_addr')
        content = msg.get('content')
    else:
        message_id = request.POST.get('sms_id')
        from_addr = request.POST.get('sender_msisdn')
        to_addr = request.POST.get('recipient_msisdn')
        content = request.POST.get('message')

    if not all([message_id, from_addr, content]):
        return HttpResponse(status=400)

    if PleaseCallMe.objects.filter(
            sender_msisdn=from_addr, message=content,
            created_at__gt=timezone.now() - timedelta(hours=2)).exists():

        # Duplicate entry
        return HttpResponse(status=409)

    PleaseCallMe.objects.create(
        user=user, sms_id=message_id, sender_msisdn=from_addr,
        recipient_msisdn=to_addr or 'default', message=content)

    return HttpResponse(status=201, content='Please Call Me registered')


@csrf_exempt
@expect_json
def events(request):
    event = request.json
    identifier = event['user_message_id'][:8]
    sms = SendSMS.objects.get(identifier=identifier)
    if event['event_type'] == 'ack':
        sms.status = 'd'  # sent
    elif event['event_type'] == 'nack':
        sms.status = 'F'  # failed
    elif event['event_type'] == 'delivery_report':
        sms.status = {
            'pending': 'd',  # sent
            'failed': 'F',  # failed
            'delivered': 'D'  # delivered
        }.get(event['delivery_status'], 'v')  # unknown
    sms.save()
    return HttpResponse(status=201, content='Event registered.')
