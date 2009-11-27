from xmlrpclib import ServerProxy, Error, ProtocolError
from datetime import datetime, timedelta
from collections import namedtuple

class IllegaleDateRange(Exception): pass

class Client(object):
    """A class abstracting the TherapyEdge XML-RPC away into something more
    approachable and less temperamental"""
    
    DEFAULT_SERVICE_URL = 'https://196.36.218.99/tools/ws/sms/patients/server.php' 
    
    # each request type is mapped to a dynamically generated class type
    TYPE_MAP = {
        'patientlist': 'Patient',
        'patients_update': 'PatientUpdate',
        'comingvisits': 'ComingVisit',
        'missedvisits': 'MissedVisit',
        'donevisits': 'DoneVisit',
        'deletedvisits': 'DeletedVisit',
    }
    
    # cache for the generated classes
    CLASS_CACHE = {}
    
    def __init__(self, uri=None, verbose=False):
        self.server = ServerProxy(uri or self.DEFAULT_SERVICE_URL, verbose=verbose)
    
    def dict_to_class(self, name, dict):
        """
        # create klass with getters & setters for parameter1 & parameter2
        klass = dict_to_class('MyClass', {'parameter1':'val1', 'parameter2':'val2'})
        # create an instance of klass with values val1 & val2
        instance = klass._make('val1','val2')
        instance.parameter1 => val1
        instance.parameter2 => val2
        """
        return self.CLASS_CACHE.setdefault(name, namedtuple(name, dict.keys()))
    
    def rpc_call(self, request, clinic_id, since='', until=''):
        """Call the XML-RPC service, returns a list of dicts"""
        # check if the given since & untils are date values, if so check their
        # sequence and manipulate them to the right format
        if isinstance(since, datetime) and isinstance(until, datetime):
            if since > until:
                raise IllegaleDateRange, 'since (%s) is greater than until (%s)' \
                                                                % (since, until)
            since = since.strftime('%Y-%m-%d')
            until = until.strftime('%Y-%m-%d')
        
        return self.server.patients_data(request, 
                                            0, # Highly magical, no clue
                                            since, 
                                            until, 
                                            3, # Highly magical, no clue
                                            clinic_id)
    
    def call_method(self, request, *args, **kwargs):
        """Call a method on the XML-RPC service, returning them as named tuples"""
        result_list = self.rpc_call(request, *args, **kwargs)
        if len(result_list):
            # convert 'patients_update' to 'PatientUpdate'
            klass_name = self.TYPE_MAP[request]
            # convert 'PatientUpdate' (str) into PatientUpdate (class)
            klass = self.dict_to_class(klass_name, result_list[0])
            # make list of dicts into PatientUpdate instances
            return map(klass._make, [d.values() for d in result_list])
        return result_list
    
    def get_all_patients(self, clinic_id):
        """Get a list of all patients available at the clinic"""
        return self.call_method('patientlist', clinic_id)
    
    def get_updated_patients(self, clinic_id, since, until=None):
        """Get a list of all patients updated between the date values given
        specified in `since` and `until`. If until is not specified it defaults
        to `datetime.now()`"""
        until = until or datetime.now()
        return self.call_method('patients_update', clinic_id, since, until)
    
    def get_coming_visits(self, *args, **kwargs):
        return self.call_method('comingvisits', *args, **kwargs)
    
    def get_missed_visits(self, *args, **kwargs):
        return self.call_method('missedvisits', *args, **kwargs)
    
    def get_done_visits(self, *args, **kwargs):
        return self.call_method('donevisits', *args, **kwargs)
    
    def get_deleted_visits(self, *args, **kwargs):
        return self.call_method('deletedvisits', *args, **kwargs)
    

