from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from txtalert.apps.gateway.models import SendSMS
from txtalert.core.utils import normalize_msisdn
from utils import read_cd4_document

# column layout in sample.xls
LAB_ID_NUMBER   = 0
MSISDN          = 1
CD4_COUNT       = 2

# CD4 message template
CD4_MESSAGE_TEMPLATE = "Hello. Thanks for doing your CD4 test. " \
                        "Your CD4 results are back. Your count is %s. " \
                        "Please report to Esselen Clinic as soon as " \
                        "possible for further treatment."

class CD4Document(models.Model):
    """An uploaded CD4Document for sending out SMSs"""
    user = models.ForeignKey(User)
    original = models.FileField(upload_to=settings.UPLOAD_ROOT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'CD4 Count Document'
    
    def send_messages(self):
        from txtalert.apps.gateway import gateway
        for cd4record in self.record_set.filter(sms__isnull=True):
            cd4record.sms = gateway.send_one_sms(self.user, 
                cd4record.msisdn,
                CD4_MESSAGE_TEMPLATE % (cd4record.cd4count, )
            )
            cd4record.save()
        
    
    def __unicode__(self):
        return u"CD4Document uploaded at %s" % (self.created_at,)
    

def load_cd4_records(sender, **kwargs):
    created = kwargs.get('created', False)
    instance = kwargs.get('instance')
    
    if created:
        for row in read_cd4_document(instance.original.path):
            normalized_msisdn = normalize_msisdn(row[MSISDN][1])
            instance.record_set.create(
                # string
                lab_id_number = row[LAB_ID_NUMBER][1],
                # Excel will probably store this as a float
                # cast to int, saved as string in db
                msisdn = normalized_msisdn,
                cd4count = row[CD4_COUNT][1]
            )

post_save.connect(load_cd4_records, sender=CD4Document)

class CD4Record(models.Model):
    """An entry in the CD4Document"""
    cd4document = models.ForeignKey(CD4Document, related_name='record_set')
    lab_id_number = models.CharField("Lab ID Number", max_length=100)
    msisdn = models.CharField("Cell phone number", max_length=11)
    cd4count = models.IntegerField("CD4 count")
    sms = models.ForeignKey(SendSMS, blank=True, null=True)
    
    class Meta:
        verbose_name = 'CD4 Count'
    
    def __unicode__(self):
        return u"%s %s" % (self._meta.verbose_name, self.lab_id_number, )
    
