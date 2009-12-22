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

from general.jquery import AutoCompleteWidget, FilteredSelectWidget

from models import *


class PleaseCallMeForm(forms.ModelForm):
    msisdn = forms.ModelChoiceField(MSISDN.objects)
    msisdn.widget = AutoCompleteWidget(
        MSISDN, 'msisdn',
        options={'minlength':5},
    )


class PleaseCallMeAdmin(admin.ModelAdmin):
    form = PleaseCallMeForm
    list_display = ('timestamp', 'msisdn','reason',)
    list_filter = ('timestamp', 'clinic','reason',)

    def queryset(self, request):
        qs = super(PleaseCallMeAdmin, self).queryset(request)
        groups = request.user.groups.all()
        # FIXME: If this fails add the Group to the admin, should have CRUD
        #        permissions for the PleaseCallMe's in TherapyEdge
        if Group.objects.get(name='Clinic Agents') in groups:
            clinics = Clinic.objects.filter(group__in=groups)
            qs = qs.filter(clinic__in=clinics)
        return qs

class PatientForm(forms.ModelForm):
    active_msisdn = forms.ModelChoiceField(
        MSISDN.objects, widget=FilteredSelectWidget('msisdns')
    )

class PatientAdmin(admin.ModelAdmin):
    form = PatientForm
    list_display = ('te_id', 'sex', 'age', 'last_clinic', 'active_msisdn')
    list_filter = ('last_clinic',)
    search_fields = ['msisdns__msisdn']

        
admin.site.register(PleaseCallMe, PleaseCallMeAdmin)
admin.site.register(Patient, PatientAdmin)

admin.site.register(MSISDN)
admin.site.register(Language)
admin.site.register(Clinic)
admin.site.register(Visit)
admin.site.register(ImportEvent)
