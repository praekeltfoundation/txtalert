# signals are auto loaded at boot
from therapyedge.models import PleaseCallMe, MSISDN, Contact
from opera.gateway import gateway
from datetime import datetime
from django.db.models import Q

def track_please_call_me(sender, **kwargs):
    """Track a number we receive from a PCM back to a specific contact. This is
    tricky because MSISDNs in txtAlert are involved in all sorts of ManyToMany 
    relationships."""
    instance = kwargs['instance']
    msisdn, _ = MSISDN.objects.get_or_create(msisdn=instance.number)
    contacts = Contact.objects.filter(active_msisdn=msisdn) or \
                msisdn.contacts.all()
    if contacts.count() == 1:
        contact = contacts[0]
        patient = contact.patient
        clinic = patient.last_clinic or patient.get_last_clinic()
        
        pcm = PleaseCallMe.objects.create(msisdn=msisdn, \
                                            timestamp=datetime.now(), \
                                            clinic=clinic)
        msg = 'Thank you for your Please Call me to %s. ' % clinic.name + \
                'An administrator will phone you back within 24 hours ' + \
                'to offer assistance.'
        gateway.send_sms([msisdn.msisdn],[msg])
    elif contacts.count() == 0:
        # not sure what to do in this situation yet
        raise Exception, 'No contacts found for MSISDN: %s' % msisdn
    else:
        # not sure what to do in this situation yet
        raise Exception, "More than one contact found for MSISDN: %s" % msisdn


def calculate_risk_profile(sender, **kwargs):
    """Calculate the risk profile of the patient after the latest visit has been
    saved to the database. This MUST be a post_save signal handler otherwise 
    the calculation will always be one visit short."""
    visit = kwargs['instance']
    patient = visit.patient
    if patient.visits.count() == 0:
        patient.last_clinic = visit.clinic
    else:
        patient.last_clinic = patient.get_last_clinic()
        missed_visits = patient.visits.filter(Q(status='m') | Q(events__status='m')).distinct().count()
        attended_visits = patient.visits.filter(Q(status='a') | Q(events__status='a')).distinct().count()
        total_visits = missed_visits + attended_visits
        if total_visits == 0:
            patient.risk_profile = 0
        else:
            patient.risk_profile =  float(missed_visits) / total_visits
        patient.save()
    