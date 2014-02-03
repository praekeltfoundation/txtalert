from django.contrib.admin.sites import AdminSite

from txtalert.core.models import Visit, Patient


site = AdminSite()


site.register(Visit)
site.register(Patient)
