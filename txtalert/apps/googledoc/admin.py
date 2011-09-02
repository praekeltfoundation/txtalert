from django.contrib import admin
from django.forms.widgets import PasswordInput


from models import SpreadSheet, GoogleAccount


class SpreadSheetAdmin(admin.ModelAdmin):
    fields = ('spreadsheet', 'account')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "account":
            if not request.user.is_superuser:
                kwargs['queryset'] = GoogleAccount.objects.filter(user=request.user)
        return super(SpreadSheetAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)
        
    def queryset(self, request):
        qs = super(SpreadSheetAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(account__user=request.user)


class GoogleAccountAdmin(admin.ModelAdmin):
    fields = ('username', 'password', )
    ordering = ('username', 'password', )
    
    def queryset(self, request):
        qs = super(GoogleAccountAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(user=request.user)
    
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
    

admin.site.register(SpreadSheet, SpreadSheetAdmin)
admin.site.register(GoogleAccount, GoogleAccountAdmin)
