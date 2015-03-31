# Create your views here.
from txtalert.core.wrhi_automation import import_visits
from django.http import HttpResponse


def testview(request):
    import_visits('http://10.0.0.3:62489/api/appad')
    return HttpResponse('ok')