from collections import namedtuple

def create_instance(klass, kwargs):
    return klass._make(klass._fields)._replace(**kwargs)


# These classes are generated on the fly by the client, the client has
# a call to class name map and reads the attribute names from the dict
# returned by TherapyEdge's XML-RPC service


Appointment = namedtuple('Apointment', [
    'fileno', 
    'phoneno',  
    'appointmentdate1', 
    'appointmentstatus1'
])

Enrol = amedtuple('Enrol', [
    'phonefileno',  
])
