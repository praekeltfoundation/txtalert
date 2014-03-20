from uuid import uuid4

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

    search_fields = ['patient__te_id', 'te_visit_id']

    fields = [
        'patient',
        'date',
        'clinic',
        'status',
        'te_visit_id',
        'comment',
    ]

    list_display = [
        'patient',
        'clinic',
        'date',
        'status',
        'visit_type',
    ]

    list_filter = [
        'date',
        'status',
        'visit_type',
    ]

    list_editable = [
        'date',
        'status',
        'visit_type',
    ]

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

    def save_model(self, request, obj, form, change):
        if not obj.te_visit_id:
            obj.te_visit_id = uuid4().hex
        return super(VisitAdmin, self).save_model(
            request, obj, form, change)


class PatientAdmin(ModelAdmin):

    readonly_fields = ('owner', 'msisdns')
    date_hierarchy = 'created_at'
    form = autocomplete_light.modelform_factory(Patient)

    search_fields = ['te_id', 'active_msisdn__msisdn', 'msisdns__msisdn']
    exclude = ['age', 'regiment', 'sex', 'disclosed', 'risk_profile']

    list_display = [
        'te_id',
        'get_display_name',
        'active_msisdn',
        # 'age',
        # 'regiment',
        # 'sex',
        'opted_in',
        # 'disclosed',
        'last_clinic',
        'next_visit',
        'last_visit',
        'language',
        'updated_at',
    ]

    list_filter = [
        'opted_in',
        'created_at',
        'updated_at',
        'language',
        'disclosed',
        'deceased',
    ]

    list_editable = [
        'opted_in',
        # 'disclosed',
        # 'active_msisdn',
        'language',
        # 'sex',
        # 'regiment',
    ]

    def get_display_name(self, obj):
        return obj.get_display_name()
    get_display_name.short_description = 'Name'

    def next_visit(self, obj):
        try:
            visit = obj.next_visit()
            return '%s @ %s' % (visit.get_status_display(), visit.date)
        except (IndexError, ValueError, AttributeError):
            return None

    def last_visit(self, obj):
        try:
            visit = obj.last_visit()
            return '%s @ %s' % (visit.get_status_display(), visit.date)
        except (IndexError, ValueError, AttributeError):
            return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "last_clinic":
            if not request.user.is_superuser:
                kwargs['queryset'] = Clinic.objects.filter(
                    user__in=users_in_same_group_as(request.user))
        return super(PatientAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

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
