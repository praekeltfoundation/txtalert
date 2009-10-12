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
from django.db import models
from django.contrib import admin
from bookingtool.models import BookingPatient
from bookingtool.widgets import RiskDateWidget
from therapyedge.models import Visit

class VisitInlineAdmin(admin.TabularInline):
    model =  Visit
    
    formfield_overrides = {
            models.DateField: {'widget': RiskDateWidget},
    }

class BookingPatientAdmin(admin.ModelAdmin):
    
    inlines = [
        VisitInlineAdmin, 
    ]
    
    form = forms.ModelForm
    list_display = ('te_id', 'surname', 'name', 'age', 'sex', 'treatment_cycle')
    list_display_links = ('te_id', 'surname', 'name')
    list_filter = ('sex', 'treatment_cycle', 'opt_status')
    ordering = ('surname', 'name')
    search_fields = ('surname', 'name', 'te_id', 'active_msisdn__msisdn')
    radio_fields = { "treatment_cycle": admin.VERTICAL, 
                        "opt_status": admin.VERTICAL,
                        "sex": admin.VERTICAL,
                    }
    save_on_top = True
    
    fieldsets = (
        (None, {
            'fields': ('active_msisdn', 'te_id', 'language', 'surname', 'name', 'sex', 'age', 'treatment_cycle', 'opt_status'),
        }),
        ('Advanced options', {
            'fields': ('last_clinic', 'risk_profile', 'date_of_birth'),
            'classes': ['collapse'],
        })
    )
    

admin.site.register(BookingPatient, BookingPatientAdmin)
