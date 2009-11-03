from django.utils import simplejson 
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet

class Resource(object):
    def dump(self):
        raise NotImplementedError


class JSONResource(Resource):
    
    def get_fields(self, instance=None, fields=None):
        return fields or \
                        getattr(self, 'fields', None) or \
                        [field.name for field in instance._meta.fields]
        
    
    def data(self, instance, fields):
        return dict([(field, getattr(instance, field)) \
                        for field in self.get_fields(instance, fields)])
    
    def dump(self, instance_or_list, fields=None):
        "left off here"
        if isinstance(instance_or_list, QuerySet):
            data = [instance for instance in instance_or_list.all()]
        if not isinstance(instance_or_list, list):
            data = [instance_or_list]
        return simplejson.dumps([self.data(instance=instance,fields=fields) \
                                    for instance in data], cls=DjangoJSONEncoder)
    
    


class SendSMSResource(JSONResource):
    
    fields = ('number', 'identifier', 'status', 'delivery', 'expiry',
                'delivery_timestamp', 'status')