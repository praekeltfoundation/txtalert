from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import AdminSite

from txtalert.core.models import Visit, Patient
from txtalert.core.admin import users_in_same_group_as


site = AdminSite()


class VisitAdmin(ModelAdmin):
    date_hierarchy = 'date'

    def queryset(self, request):
        qs = super(VisitAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user__in=users_in_same_group_as(request.user))

site.register(Visit, VisitAdmin)
site.register(Patient)
