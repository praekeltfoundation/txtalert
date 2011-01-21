from collections import namedtuple

def create_instance(klass, kwargs):
    return klass._make(klass._fields)._replace(**kwargs)


# These classes are generated on the fly by the client, the client has
# a call to class name map and reads the attribute names from the dict
# returned by TherapyEdge's XML-RPC service

PatientUpdate = namedtuple('PatientUpdate', [
    'dr_site_name', 
    'dr_site_id', 
    'age', 
    'sex', 
    'celphone',  # TherapyEdge's typo
    'dr_status', 
    'te_id'
])

ComingVisit = namedtuple('ComingVisit', [
    'dr_site_name',
    'dr_site_id',
    'dr_status',
    'scheduled_visit_date',
    'key_id',
    'te_id'
])

MissedVisit = namedtuple('MissedVisit', [
    'dr_site_name',
    'dr_site_id',
    'missed_date', 
    'dr_status', 
    'key_id', 
    'te_id'
])

DoneVisit = namedtuple('DoneVisit', [
    'done_date', 
    'dr_site_id', 
    'dr_status', 
    'dr_site_name', 
    'scheduled_date', 
    'key_id', 
    'te_id'
])

DeletedVisit = namedtuple('DeletedVisit', [
    'key_id',
    'dr_status',
    'dr_site_id',
    'te_id',
    'dr_site_name'
])