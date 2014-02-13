from datetime import timedelta
from functools import wraps
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone

from txtalert.apps.gateway.models import PleaseCallMe


def expect_json(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.META.get('CONTENT_TYPE') == 'application/json':
            request.json = json.load(request)
        else:
            request.json = None
        return func(request, *args, **kwargs)

    return wrapper


@login_required
@expect_json
def pcm(request):
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

    if not all([message_id, from_addr, to_addr, content]):
        return HttpResponse(status=400)

    if PleaseCallMe.objects.filter(
            sender_msisdn=from_addr, message=content,
            created_at__gt=timezone.now() - timedelta(hours=2)).exists():

        # Duplicate entry
        return HttpResponse(status=409)

    PleaseCallMe.objects.create(
        user=request.user, sms_id=message_id, sender_msisdn=from_addr,
        recipient_msisdn=to_addr, message=content)

    return HttpResponse(status=201, content='Please Call Me registered')
