from django.conf import settings
from txtalert.apps.gateway.models import SendSMS

class CD4Document(models.Model):
    """An uploaded CD4Document for sending out SMSs"""
    original = models.FileField(upload_to=settings.UPLOAD_ROOT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return u"CD4Document uploaded at %s" % (self.created,)
    

class CD4Record(models.Model):
    """An entry in the CD4Document"""
    lab_id_number = models.CharField("Lab ID Number", blank=False, max_length=100)
    msisdn = models.PhoneNumberField("Cell phone number")
    cd4count = models.IntegerField("CD4 count")
    sms = models.ForeignKey("SMS", SendSMS)
    
    def __unicode__(self):
        return u"CD4Record %s" % (self.lab_id_number, )
    
