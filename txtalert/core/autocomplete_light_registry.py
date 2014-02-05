import autocomplete_light

from txtalert.core.models import Patient, Visit


autocomplete_light.register(Patient, search_fields=['te_id'])
autocomplete_light.register(Visit, search_fields=['te_visit_id'])
