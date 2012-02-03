#  This file is part of TxtAlert.
#
#  TxtALert is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TxtAlert is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with TxtAlert.  If not, see <http://www.gnu.org/licenses/>.


from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group

from txtalert.apps.general.jquery import AutoCompleteWidget, FilteredSelectWidget

from models import *

def users_in_same_group_as(user):
    groups = user.groups.all()
    groups_users = User.objects.distinct().filter(groups__in=groups)
    return groups_users

class PleaseCallMeForm(forms.ModelForm):
    msisdn = forms.ModelChoiceField(MSISDN.objects)
    msisdn.widget = AutoCompleteWidget(
        MSISDN, 'msisdn',
        options={'minlength':5},
    )


class PleaseCallMeAdmin(admin.ModelAdmin):
    form = PleaseCallMeForm
    list_display = ('timestamp', 'msisdn','reason','notes', 'message')
    list_filter = ('timestamp', 'clinic','reason',)
    readonly_fields = ('user',)

    def queryset(self, request):
        qs = super(PleaseCallMeAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(user__in=users_in_same_group_as(request.user))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "clinic":
            if not request.user.is_superuser:
                kwargs['queryset'] = Clinic.objects.filter(user__in=users_in_same_group_as(request.user))
        return super(PleaseCallMeAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)


class PatientForm(forms.ModelForm):
    active_msisdn = forms.ModelChoiceField(
        MSISDN.objects, widget=FilteredSelectWidget('msisdns')
    )

class PatientAdmin(admin.ModelAdmin):
    form = PatientForm
    list_display = ('te_id', 'sex', 'age', 'last_clinic', 'active_msisdn')
    list_filter = ('last_clinic',)
    search_fields = ['msisdns__msisdn', 'te_id', 'name', 'surname']
    readonly_fields = ('owner','last_clinic',)

    def queryset(self, request):
        qs = super(PatientAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            qs = qs.filter(owner__in=users_in_same_group_as(request.user))
            return qs

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.owner = request.user
        else:
            try:
                obj.owner
            except User.DoesNotExist:
                obj.owner = request.user
        obj.save()


class VisitAdmin(admin.ModelAdmin):
    readonly_fields = ('patient','clinic', 'te_visit_id')
    exclude = ('deleted',)
    def queryset(self, request):
        qs = super(VisitAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(patient__owner__in=users_in_same_group_as(request.user))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "patient":
            if not request.user.is_superuser:
                kwargs['queryset'] = Patient.objects.filter(owner=users_in_same_group_as(request.user))
        return super(VisitAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)



class MessageTypeAdmin(admin.ModelAdmin):
    list_filter = ('group', 'language', 'name')

admin.site.register(PleaseCallMe, PleaseCallMeAdmin)
admin.site.register(Patient, PatientAdmin)

admin.site.register(MSISDN)
admin.site.register(Language)
admin.site.register(Clinic)
admin.site.register(Visit, VisitAdmin)
admin.site.register(Event)
admin.site.register(MessageType, MessageTypeAdmin)