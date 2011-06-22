from django.core.management.base import BaseCommand
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

def normalize_msisdn(raw):
    raw = str(int(raw))
    if raw.startswith('0'):
        return '27' + raw[1:]
    if raw.startswith('+'):
        return raw[1:]
    if raw.startswith('27'):
        return raw
    return '27' + raw

class MuninCommand(BaseCommand):
    def handle(self, *args, **kwargs):
        if args and args[0] == "config":
            return self.config()
        else:
            return self.run()
    
    def output(self, _dict):
        print "\n".join(["%s %s" % (k,v) for k,v in _dict.items()])
    
    def config(self):
        raise NotImplementedError
    
    def run(self):
        raise NotImplementedError
    