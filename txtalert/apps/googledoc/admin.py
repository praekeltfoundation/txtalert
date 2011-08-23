from django.contrib import admin

from models import SpreadSheet, GoogleAccount


class SpreadSheetAdmin(admin.ModelAdmin):
    fields = ('spreadsheet', 'account',)
    
class GoogleAccountAdmin(admin.ModelAdmin):
    fields = ('username', 'password', )
    ordering = ('username', 'password', )


admin.site.register(SpreadSheet, SpreadSheetAdmin)
admin.site.register(GoogleAccount, GoogleAccountAdmin)