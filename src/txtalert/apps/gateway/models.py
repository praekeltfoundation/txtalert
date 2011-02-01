from django.db import models
from django.contrib.auth.models import User

# Copied from https://dragon.sa.operatelecom.com:1089/Gateway#Receipt, seems sensible to keep for now
RECEIPT_STATUS_CHOICES = (
    ('D', 'Delivered'), # message confirmed as delivered to handset.
    ('d', 'Sent'), # message sent to network operator aggregator and accepted by them. This will appear in a delivery receipt when the network operator or aggregaator does not support delivery receipts (so the best/only information we have about message delivery is that they accepted the message).
    ('E', 'Expired'), # message lifetime expired before delivery (during or after sending to the network or aggregator).
    ('e', 'BillingExpired'), # message not sent (message lifetime expired before billing was done, or the maximum number of billing retry attempts was reached).
    ('F', 'Failed'), # message sent, but network or aggregator failed the message without additional failure information.
    ('1', 'HandsetOff'), # message sent but failed because handset is turned off.
    ('2', 'HandsetFull'), # message sent but failed because handset is full.
    ('3', 'HandsetDead'), # message sent but failed because handset is dead.
    ('4', 'HandsetBarred'), # message sent but failed because handset is barred.
    ('5', 'HandsetError'), # message sent but failed because of a handset error.
    ('6', 'UnusableChannel'), # message not sent (attempt to send on a channel which is not configured for that type of message)
    ('7', 'UnusableNetwork'), # message not sent (attempt to send on a channel which is not configured to send to the given network)
    ('8', 'Unbillable'), # message not sent (network or aggregator's billing system does not recognise the phone number etc). In this case the problem may be that the message was sent to the wrong network.
    ('9', 'InsufficientFunds'), # message not sent (handset reported as out of funds (or having exceeded a credit limit) by network or aggregator's billing system). The system's re-billing mechanism comes in to play here and tries to re-bill the customer, but if the re-billing attempts fail, then the message will fail with this status.
    ('C', 'BillingBarred'), # message not sent (network or aggregator has barred/blacklisted billing for this number, or perhaps a monthly (or other long term) credit limit has been reached). The system does not attempt re-billing in this case as it is assumed that the number is unlikely to start working again in the short term.
    ('c', 'BillingCancelled'), # message not sent because the customer cancelled the billing operation (or failed to grant permission for it).
    ('b', 'Unbilled'), # message not sent (billing attempt refused by network or aggregator's billing system). A generic failure status produced when the network operator or aggregator does not give information about the reason for the billing failure.
    ('I', 'Failed'), # message not sent (client had insufficient credit on the local system). If this occurs, the client needs to contact the local system administration to obtain more credit.
    ('Q', 'Queued'), # waiting to be sent to network operator or aggregator, or an incoming (MO) message waiting to be handled by a local service.
    ('P', 'Progress'), # the message is in progress of being sent to the network operator or aggregator, but has not yet been acknowledged by them.
    ('B', 'Billing'), # billing for the message has been queued and the system is waiting for that to complete before sending the message.
    ('R', 'Received'), # incoming (MO) message handled by local servic('e', '('r', 'Replaced ... this message was sent and replaced an earlier one at the network operator or aggregator's message centr('e', '('U', 'Unrecognised ... message sent but rejected by network or aggregator, perhaps because the handset is on a different network.
    ('u', 'Unsent'), # an attempt has been made to send the message, but that did not work and the system is waiting a while before retryin('g', '('V', 'Viewed ... the message has been received by the handset and has been displayed.
    ('v', 'Unknown'), # network operator or aggregator failed to acknowledge the message submission, so the message may have been delivered but probably has not.
    ('A', 'Billing unknown'), # network operator or aggregator failed to acknowledge a billing attempt, so the billing operation may have taken place but probably has not. The customer should not be re-billed without checking with them to see if the network operator has billed them.
)

class SendSMS(models.Model):
    """A local storage of SMS's sent via the SendSMS API, need to keep 
    track of these to be able to process the receipts we receive asynchronously
    back from the WASP"""
    
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
    
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
    
    user = models.ForeignKey(User)
    msisdn = models.CharField(max_length=12)
    smstext = models.TextField()
    delivery = models.DateTimeField()
    expiry = models.DateTimeField()
    priority = models.CharField(max_length=80, choices=PRIORITY_CHOICES)
    receipt = models.CharField(max_length=1, choices=RECEIPT_CHOICES)
    identifier = models.CharField(blank=False, max_length=8)
    status = models.CharField(max_length=1, default='v', choices=RECEIPT_STATUS_CHOICES)
    delivery_timestamp = models.DateTimeField(null=True)
    
    class Meta:
        permissions = (
            ('can_view_sms_statistics', 'Can view SMS statistics'),
            ('can_send_sms', 'Can send SMSs'),
            ('can_place_sms_receipt', 'Can place SMS receipt'),
        )
        get_latest_by = 'id'
    
    def __unicode__(self):
        return u"SendSMS: %s - %s" % (self.identifier, self.msisdn)


class PleaseCallMe(models.Model):
    """A please call me we receive from a patient"""
    user = models.ForeignKey(User, related_name='gateway_pleasecallme_set')
    sms_id = models.CharField(max_length=80)
    sender_msisdn = models.CharField(max_length=255)
    recipient_msisdn = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name, verbose_name_plural = "Please Call Me", "'Please Call Me's"
        permissions = (
            ('can_place_pcm', 'Can place a PCM'),
            ('can_view_pcm_statistics', 'Can view PCM statistics'),
        )

    def __unicode__(self):
        return u"PleaseCallMe: %s" % self.sender_msisdn

