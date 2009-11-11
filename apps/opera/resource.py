from simpleresource import Resource

class SendSMSResource(Resource):
    
    # fields being exposed via JSON or XML
    fields = ('identifier', 'delivery', 'expiry', 'delivery_timestamp', \
                 'status', 'status_display', 'number')
    
    # the root element if the exposing format so requires it, XML for example
    root = "send-sms"
    
    def status_display(self, instance):
        return instance.get_status_display()


class PleaseCallMeResource(Resource):
    """Resource for exposing PleaseCallMe's over HTTP"""
    fields = ('sms_id', 'number', 'created_at')
    root = 'please-call-me'
    