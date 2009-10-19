import hashlib
from mobile.sms.models import Gateway
from datetime import datetime

class TestingGateway(Gateway):
    """Dummy gateway for mimicking SMSs being sent, allows us to test the 
    outgoing traffic to Opera or whatever gateway we're using"""
    
    class Meta:
        proxy = True
    
    @property
    def queue(self):
        if not hasattr(self, '_queue'):
            self._queue = {}
        return self._queue
    
    def sendSMS(self, msisdns, message):
        self.queue[message] = msisdns
        return self.logAction(datetime.now(), datetime.now(), \
                                        [(m, 'u') for m in msisdns], message)
    


def random_string(val=None):
    if not val: val = datetime.now()
    m = hashlib.sha1()
    m.update(str(val))
    return m.hexdigest()


