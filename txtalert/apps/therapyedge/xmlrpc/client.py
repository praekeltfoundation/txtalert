from xmlrpclib import ServerProxy, Error, ProtocolError
from datetime import datetime, timedelta
from collections import namedtuple


class IllegalDateRange(Exception):
    pass


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

    def create_instances_of(self, klass, iterable):
        """This is sort of kludgy. We get a dict from TherapyEdge and in turn
        read the values from that dict to populate a class instance. We're
        expecting that TherapyEdge will not change the order of the dict and that
        the order of the values are always consistent. This isn't true and as such
        we should be populating the instances by explicitly passing in the values
        instead of iterating over a list of unreliable ordering.

        Ugh, this is sketchy at best
        """
        for item in iterable:
            # create empty instance with empty values
            instance = klass._make(klass._fields)
            # named tuples won't allow the setting of variables but will allow
            # replacing them with a new set of vars and which returns a new
            # instance of the named tuple
            yield instance._replace(**item)

    def call_method(self, request, *args, **kwargs):
        """Call a method on the XML-RPC service, returning them as named tuples"""
        # result_list = self.rpc_range_call(request, *args, **kwargs)
        result_list = self.server.patients_data(request, *args, **kwargs)
        if result_list:
            # convert 'patients_update' to 'PatientUpdate'
            klass_name = self.TYPE_MAP[request]
            # convert 'PatientUpdate' (str) into PatientUpdate (class)
            klass = self.dict_to_class(klass_name, result_list[0])
            # make list of dicts into PatientUpdate instances
            return self.create_instances_of(klass, result_list)
        return result_list

    def get_all_patients(self):
        """Get a list of all patients available at the clinic"""
        return self.call_method('patientlist')

    def get_updated_patients(self, since):
        """Get a list of all patients updated since `since`. """
        return self.call_method('patients_update', 'update_date', since)

    def call_range_method(self, request, since, until, visit_type):
        if since > until:
            raise IllegalDateRange(
                'since (%s) is greater than until (%s)' % (since, until))
        return self.call_method(request, 'date_range',
                                since.strftime('%Y-%m-%d'),
                                until.strftime('%Y-%m-%d'),
                                visit_type)

    def get_coming_visits(self, since, until, visit_type):
        return self.call_range_method('comingvisits', since, until, visit_type)

    def get_missed_visits(self, since, visit_type):
        # TherapyEdge will return scheduled but unattended future visits as missed
        # So we can't ask for missed visits after midnight last night
        # Therefore the 'until' parameter (args[2]), must be reset to midnight
        midnight = datetime.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
        return self.call_range_method('missedvisits', since, midnight,
                                      visit_type)

    def get_done_visits(self, since, until, visit_type):
        return self.call_range_method('donevisits', since, until, visit_type)

    def get_deleted_visits(self, since, until, visit_type):
        return self.call_range_method('deletedvisits', since, until,
                                      visit_type)



# def introspect(client, *args, **kwargs):
#     methods = [
#         'get_all_patients',
#         'get_updated_patients',
#         'get_coming_visits',
#         'get_missed_visits',
#         'get_done_visits',
#         'get_deleted_visits'
#     ]
#     for method in methods:
#         try:
#             meth = getattr(client, method)
#             results = meth(*args, **kwargs)
#             if results:
#                 print 'method:', method, 'records:', len(results), 'of type:', results[0]
#             else:
#                 print method, 'returned an empty set'
#         except ProtocolError, e:
#             print method, 'raised a ProtocolError', e
#
#
# if __name__ == '__main__':
#     import os
#     from datetime import datetime, timedelta
#     uri = 'https://%s:%s@196.36.218.99/tools/ws/sms/patients/server.php' % (
#         os.environ['THERAPYEDGE_USERNAME'],
#         os.environ['THERAPYEDGE_PASSWORD']
#     )
#
#     kwargs = {
#         'clinic_id': '02',  # magical I know, i think this is the Themba Lethu Clinic
#         'since': datetime.now() - timedelta(days=2),
#         'until': datetime.now() + timedelta(days=2)
#     }
#
#     print "Introspecting with uri: %s" % uri
#     print "                  args: %s" % kwargs
#     introspect(Client(uri), **kwargs)
