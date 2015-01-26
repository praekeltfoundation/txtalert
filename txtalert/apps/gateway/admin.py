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


from django.contrib import admin
from models import SendSMS, PleaseCallMe


class PleaseCallMeAdmin(admin.ModelAdmin):
    list_display = ('sender_msisdn', 'recipient_msisdn','message','created_at')
    list_filter = ('created_at',)


class SendSMSAdmin(admin.ModelAdmin):
    list_display = ('msisdn', 'user','smstext', 'delivery', 'status', 'delivery_timestamp', 'identifier')
    list_filter = ('msisdn',)


admin.site.register(SendSMS, SendSMSAdmin)
admin.site.register(PleaseCallMe, PleaseCallMeAdmin)