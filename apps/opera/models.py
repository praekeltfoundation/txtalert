from django.db import models

# Create your models here.
class SendSMS(models.Model):
    """A local storage of SMS's sent via the SendSMS API, need to keep 
    track of these to be able to process the receipts we receive back from
    Opera"""
    
    PRIORITY_CHOICES = (
        ('Urgent', 'Urgent'),
        ('Interactive', 'Interactive'),
        ('Standard', 'Standard'),
        ('Bulk', 'Bulk'),
    )
    
    RECEIPT_CHOICES = (
        ('Y', 'Yes'),
        ('N', 'No'),
    )
    
    numbers = models.TextField()
    smstexts = models.TextField()
    delivery = models.DateTimeField()
    expiry = models.DateTimeField()
    priority = models.CharField(max_length=80, choices=PRIORITY_CHOICES)
    receipt = models.CharField(max_length=2, choices=RECEIPT_CHOICES)
    identifier = models.CharField(blank=False, max_length=8)
    
    def __unicode__(self):
        return u"SendSMS %s" % self.identifier
    
    @models.permalink
    def get_absolute_url(self):
        return ('SendSMS', [self.id])
    

