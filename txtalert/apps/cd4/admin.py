from django.contrib import admin, messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns
from .models import *

def get_sms_delivery(cd4record):
    if cd4record.sms:
        return cd4record.sms.delivery.strftime("%c")
    return ''
get_sms_delivery.short_description = "SMS sent at"

def get_sms_status_display(cd4record):
    if cd4record.sms:
        return cd4record.sms.get_status_display()
    return ''
get_sms_status_display.short_description = "Delivery status"


class CD4DocumentRecordInlineAdmin(admin.TabularInline):
    model = CD4Record
    extra = 0
    exclude = ('sms',)
    can_delete = False
    readonly_fields = ('lab_id_number',
                        # 'msisdn',
                        'cd4count',
                        get_sms_delivery, 
                        get_sms_status_display)
    

class CD4DocumentAdmin(admin.ModelAdmin):
    inlines = [
        CD4DocumentRecordInlineAdmin
    ]
    readonly_fields = ['created_at', 'user']
    list_filter = ['created_at',]
    
    def get_urls(self):
        urls = super(CD4DocumentAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^send/(?P<object_id>\d+)/$', self.admin_site.admin_view(self.send_cd4_messages),
                {}, "send_cd4_messages"),
        )
        return my_urls + urls
    
    def send_cd4_messages(self, request, object_id):
        document = get_object_or_404(CD4Document, pk=object_id)
        document.send_messages()
        messages.add_message(request, messages.INFO, 'SMS messages sent succesfully.')
        return HttpResponseRedirect(reverse('admin:cd4_cd4document_change', 
            args=(object_id,)))
    
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
    
    def change_view(self, request, object_id, extra_context=None):
        if request.POST.has_key('_send_cd4_messages'):
            return self.send_cd4_messages(request, object_id)
        return super(CD4DocumentAdmin, self).change_view(request, object_id, 
            extra_context)

admin.site.register(CD4Document, CD4DocumentAdmin)
