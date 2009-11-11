from django.db.models.query import QuerySet
from publishers import XMLResourcePublisher, JSONResourcePublisher
import types

class Resource(object):
    
    formats = {
        "xml": XMLResourcePublisher,
        "json": JSONResourcePublisher,
    }
    
    model = None
    
    def __init__(self, instance_or_list, fields=None):
        self.list = self.normalize_to_list(instance_or_list)
        self.fields = fields or getattr(self, 'fields', None) or \
                        self.get_fields_from_model(self.list[0])
    
    def normalize_to_list(self, instance_or_list):
        if isinstance(instance_or_list, QuerySet):
            return list(instance_or_list)
        elif isinstance(instance_or_list, types.ListType):
            return instance_or_list
        else:
            return [instance_or_list]
    
    def get_fields_from_instance(self, instance):
        return [field.name for field in instance._meta.fields]

    def field_data_for_instance(self, instance):
        return dict([(field, self.value_for_field(instance, field)) \
                                                    for field in self.fields])
    
    def is_instance_field(self, instance, field):
        return field in self.get_fields_from_instance(instance)
    
    def get_instance_field_value(self, instance, field_name):
        field = instance._meta.get_field(field_name)
        return field.value_to_string(instance)
    
    def value_for_field(self, instance, field):
        if self.is_instance_field(instance, field):
            return self.get_instance_field_value(instance, field)
        else:
            return getattr(self, field)(instance)
    
    def get_root_from_model(self):
        return self.model._meta.module_name
    
    def get_root(self):
        return getattr(self, 'root', self.get_root_from_model())
    
    def publish(self, format):
        if format in self.formats:
            data = [self.field_data_for_instance(instance) for instance in self.list]
            klass = self.formats[format]
            return klass().publish(data, root=self.get_root())
        else:
            raise NotImplementedError
    
