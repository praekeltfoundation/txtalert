from django.contrib import admin

from models import SpreadSheet


class SpreadSheetAdmin(admin.ModelAdmin):
    fields = ('spreadsheet',)


admin.site.register(SpreadSheet, SpreadSheetAdmin)