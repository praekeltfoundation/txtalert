from collections import namedtuple
from datetime import datetime
import hashlib

def create_instance(klass, kwargs):
    return klass._make(klass._fields)._replace(**kwargs)


def random_string(val=None):
    if not val: val = datetime.now()
    m = hashlib.sha1()
    m.update(str(val))
    return m.hexdigest()
