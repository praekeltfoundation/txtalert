import autocomplete_light

from txtalert.core.models import Patient, Visit
from txtalert.core.admin import users_in_same_group_as


class PatientAutoComplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['te_id']
    model = Patient

    def choices_for_request(self):
        if not self.request.user.is_superuser:
            self.choices = self.choices.filter(
                owner__in=users_in_same_group_as(self.request.user))
        return super(PatientAutoComplete, self).choices_for_request()


class VisitAutoComplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['te_visit_id']
    model = Visit

    def choices_for_request(self):
        if not self.request.user.is_superuser:
            self.choices = self.choices.filter(
                user__in=users_in_same_group_as(self.request.user))
        return super(VisitAutoComplete, self).choices_for_request()


autocomplete_light.register(Patient, PatientAutoComplete)
autocomplete_light.register(VisitAutoComplete)
