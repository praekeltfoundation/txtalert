from django.contrib import admin
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


admin.site.register(CD4Document, CD4DocumentAdmin)