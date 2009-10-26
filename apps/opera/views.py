from django.http import HttpResponse

# Create your views here.
def receipt(request):
    if request.POST:
        print request.raw_post_data
    else:
        print 'called without POST'
    return HttpResponse('ok!')