from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required

@permission_required('core.add_patient', login_url='/bookings/admin/sign-in/')
def index(request):
    return HttpResponse("hello")