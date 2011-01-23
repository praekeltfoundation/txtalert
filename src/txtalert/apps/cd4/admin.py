from django.contrib import admin
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns
from .models import *

class CD4DocumentRecordInlineAdmin(admin.TabularInline):
    model = CD4Record
    extra = 0
    readonly_fields = ['sms']

class CD4DocumentAdmin(admin.ModelAdmin):
    inlines = [
        CD4DocumentRecordInlineAdmin
    ]
    readonly_fields = ['group', 'created_at']
    list_filter = ['created_at',]
    
    def get_urls(self):
        urls = super(CD4DocumentAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^send/(?P<object_id>\d+)/$', self.admin_site.admin_view(self.send_messages), 
                {}, 'send_messages'),
        )
        return my_urls + urls
    
    def send_messages(self, request, object_id):
        document = get_object_or_404(CD4Document, pk=object_id)
        document.send_messages()
        messages.add_message(request, messages.INFO, 'SMS messages sent succesfully.')
        return HttpResponseRedirect(reverse('admin:cd4_cd4_document_change', 
            args=(object_id,)))
    

admin.site.register(CD4Document, CD4DocumentAdmin)