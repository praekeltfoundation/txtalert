from txtalert.core.models import ChangeRequest, PleaseCallMe

def change_requests(request):
    return {
        'change_requests': ChangeRequest.objects.filter(status='pending'),
        'call_requests': PleaseCallMe.objects.filter().order_by('-timestamp')
    }
