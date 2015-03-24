# Create your views here.
from txtalert.core.wrhi_automation import import_patients
from django.http import HttpResponse


def testview(request):
    import_patients('http://10.0.0.4:62489/api/appad')
    return HttpResponse('ok')