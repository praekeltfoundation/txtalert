from therapyedge.models import PleaseCallMe, MSISDN, Contact
from gateway import gateway
from datetime import datetime
from django.db.models import Q

import logging
logger = logging.getLogger("signals")

def track_please_call_me_handler(sender, **kwargs):
    return track_please_call_me(kwargs['instance'])

def track_please_call_me(opera_pcm):
    """Track a MSISDN we receive from a PCM back to a specific contact. This is
    tricky because MSISDNs in txtAlert are involved in all sorts of ManyToMany 
    relationships."""
    msisdn, _ = MSISDN.objects.get_or_create(msisdn=opera_pcm.sender_msisdn)
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
        logger.error('track_please_call_me: No contacts found for MSISDN: %s' % msisdn)
    else:
        # not sure what to do in this situation yet
        logger.error("track_please_call_me: More than one contact found for MSISDN: %s" % msisdn)


def calculate_risk_profile_handler(sender, **kwargs):
    return calculate_risk_profile(kwargs['instance'])

def calculate_risk_profile(visit):
    """Calculate the risk profile of the patient after the latest visit has been
    saved to the database. This MUST be a post_save signal handler otherwise 
    the calculation will always be one visit short."""
    # FIXME, the main argument should be the Patient not the Visit, this method
    #        is being too clever
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


def check_for_opt_in_changes_handler(sender, **kwargs):
    return check_for_opt_in_changes(kwargs['instance'])

def check_for_opt_in_changes(patient):
    """Check the dirty state of a patient, has the opt-in status changed 
    compared to the state as known in the DB. This MUST be called as a pre_save
    signal otherwise the dirty state tells us nothing."""
    if 'opted_in' in patient.get_dirty_fields():
        # here we should notify api client of the change in opt-in status 
        # mb via an HTTP push
        pass
    


def update_contact_active_msisdn_handler(sender, **kwargs):
    return update_contact_active_msisdn(kwargs['instance'])

def update_contact_active_msisdn(patient):
    """Update the patients active_msisdn with the first in the list
    of available options if none have been set yet"""
    msisdns = patient.msisdns.all()
    if not patient.active_msisdn and msisdns.count() > 0:
        patient.active_msisdn = msisdns[0]
        patient.save()


def find_clinic_for_please_call_me_handler(sender, **kwargs):
    return find_clinic_for_please_call_me(kwargs['instance'])

def find_clinic_for_please_call_me(pcm):
    if not pcm.clinic:
        patient = Patient.objects.get(id=pcm.msisdn.contacts.all()[0].id)
        pcm.clinic = patient.get_last_clinic()


def update_visit_status_handler(sender, **kwargs):
    return update_visit_status(kwargs['instance'])

def update_visit_status(visit_event):
    # Fixme: magical slicing, unclear what's going on
    if visit_event.date == visit_event.visit.events.order_by('-date')[:1][0].date:
        visit_event.visit.status = visit_event.status
        visit_event.visit.save()

    