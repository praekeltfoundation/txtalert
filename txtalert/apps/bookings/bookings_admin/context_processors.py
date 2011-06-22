from txtalert.core.models import ChangeRequest

def change_requests(request):
    return {
        'change_requests': ChangeRequest.objects.filter(status='pending')
    }
        