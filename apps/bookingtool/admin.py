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
from bookingtool.models import BookingPatient

class BookingPatientAdmin(admin.ModelAdmin):
    form = forms.ModelForm
    list_display = ('te_id', 'mrs_id', 'surname', 'name', 'age', 'sex', 'treatment_cycle')
    list_display_links = ('te_id', 'mrs_id', 'surname', 'name')
    list_filter = ('sex', 'treatment_cycle', 'opt_status')
    ordering = ('surname', 'name')
    search_fields = ('surname', 'name', 'te_id', 'mrs_id', 'active_msisdn__msisdn')
    radio_fields = { "treatment_cycle": admin.VERTICAL, 
                        "opt_status": admin.VERTICAL,
                        "sex": admin.VERTICAL,
                    }
    save_on_top = True
    

admin.site.register(BookingPatient, BookingPatientAdmin)
