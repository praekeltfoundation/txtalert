from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User

import autocomplete_light

from txtalert.core.models import Visit, Patient, Clinic, MSISDN
from txtalert.core.admin import users_in_same_group_as


site = AdminSite(name="clinic-admin")


class VisitAdmin(ModelAdmin):
    date_hierarchy = 'date'
    form = autocomplete_light.modelform_factory(Visit)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "clinic":
            if not request.user.is_superuser:
                kwargs['queryset'] = Clinic.objects.filter(
                    user__in=users_in_same_group_as(request.user))
        elif db_field.name == "patient":
            if not request.user.is_superuser:
                kwargs['queryset'] = Patient.objects.filter(
                    owner__in=users_in_same_group_as(request.user))
        return super(VisitAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    def queryset(self, request):
        qs = super(VisitAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(
            patient__owner__in=users_in_same_group_as(request.user))


class PatientAdmin(ModelAdmin):
    date_hierarchy = 'created_at'
    form = autocomplete_light.modelform_factory(Patient)

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


site.register(Visit, VisitAdmin)
site.register(Patient, PatientAdmin)
site.register(MSISDN)
