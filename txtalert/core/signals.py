from txtalert.core.models import PleaseCallMe, MSISDN, Visit, Patient
from datetime import datetime
from django.db.models import Q
import logging

def track_please_call_me_handler(sender, **kwargs):
    if kwargs.get('created', False):
        return track_please_call_me(kwargs['instance'])

def sloppy_get_or_create_possible_msisdn(sloppy_formatted_msisdn):
    # if the msisdn is of fewer characters than 9 then don't normalize
    # as it's a shortcode or a special number like 121 / voicemail.
    if len(sloppy_formatted_msisdn) < 9:
        msisdn, created = MSISDN.objects.get_or_create(msisdn=sloppy_formatted_msisdn)
        return msisdn
    
    # Assume the MSISDNs are always formatted as +27761234567, normalize
    # to 761234567
    end_of_msisdn = sloppy_formatted_msisdn[-9:]
    
    # it could be formatted as 27761234567,+27761234567 or 0761234567
    possible_msisdns = MSISDN.objects.filter(msisdn__endswith=end_of_msisdn)
    if possible_msisdns.exists():
        # priority for an MSISDN with a patient set
        for msisdn in possible_msisdns:
            if msisdn.patient_set.exists():
                return msisdn # just so you know what's going on
        # otherwise we'll settle for a patient that has used this MSISDN 
        # previously
        for msisdn in possible_msisdns:
            if msisdn.contacts.exists():
                return msisdn
        
        # all possible MSISDNs have no patients linked to them
        # if that's the case then just default to the most recent
        # MSISDN registered for that given number.
        return possible_msisdns.latest('id')
    # nothing matches, so create one
    else:
        msisdn, created = MSISDN.objects.get_or_create(msisdn=sloppy_formatted_msisdn)
        return msisdn


def track_please_call_me(opera_pcm):
    """Track a MSISDN we receive from a PCM back to a specific contact. This is
    tricky because MSISDNs in txtAlert are involved in all sorts of ManyToMany 
    relationships."""
    msisdn = sloppy_get_or_create_possible_msisdn(opera_pcm.sender_msisdn)
    patients = Patient.objects.filter(active_msisdn=msisdn) or \
                msisdn.contacts.all()
    if patients.count() == 1:
        patient = patients[0]
        clinic = patient.last_clinic or patient.get_last_clinic()
    
        pcm = PleaseCallMe.objects.create(msisdn=msisdn,
                                            timestamp=datetime.now(),
                                            clinic=clinic,
                                            user=opera_pcm.user,
                                            message=opera_pcm.message)
        logging.info("track_please_call_me: PCM registered for %s at %s for clinic %s from opera PCM: %s" % (
            pcm.msisdn,
            pcm.timestamp,
            pcm.clinic,
            opera_pcm
        ))
        # msg = 'Thank you for your Please Call Me. ' + \
        #         'An administrator will phone you back within 24 hours ' + \
        #         'to offer assistance.'
        # from gateway import gateway
        # gateway.send_sms([msisdn.msisdn],[msg])
    elif patients.count() == 0:
        # not sure what to do in this situation yet, lets minimally store the PCM
        # so we don't loose track of any.
        pcm = PleaseCallMe.objects.create(msisdn=msisdn,
                                            timestamp=datetime.now(),
                                            user=opera_pcm.user, 
                                            message=opera_pcm.message)
        logging.info('track_please_call_me: No contacts found for MSISDN: %s, registering without clinic.' % msisdn)
    else:
        # not sure what to do in this situation yet, lets minimally store the PCM
        # so we don't loose track of any.
        pcm = PleaseCallMe.objects.create(msisdn=msisdn,
                                            timestamp=datetime.now(),
                                            user=opera_pcm.user,
                                            message=opera_pcm.message)
        logging.info("track_please_call_me: More than one contact found for MSISDN: %s" % msisdn)


def calculate_risk_profile_handler(sender, **kwargs):
    return calculate_risk_profile(kwargs['instance'])

def calculate_risk_profile(visit):
    """Calculate the risk profile of the patient after the latest visit has been
    saved to the database. This MUST be a post_save signal handler otherwise 
    the calculation will always be one visit short."""
    patient = visit.patient
    patient.last_clinic = patient.get_last_clinic()
    missed_visits = Visit.history.filter(patient=patient, status='m').count()
    attended_visits = Visit.history.filter(patient=patient, status='a').count()
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
        logging.debug('I should push changes somewhere')
    


def find_clinic_for_please_call_me_handler(sender, **kwargs):
    return find_clinic_for_please_call_me(kwargs['instance'])

def find_clinic_for_please_call_me(pcm):
    if not pcm.clinic:
        # this is hacky at best, we're not sure this will even return results.
        contacts_for_msisdn = pcm.msisdn.contacts.all()
        if contacts_for_msisdn:
            patient = Patient.objects.get(id=contacts_for_msisdn[0].pk)
            pcm.clinic = patient.get_last_clinic()
        else:
            logging.info("find_clinic_for_please_call_me: Unable to determine clinic for %s" % pcm.msisdn)


def update_active_msisdn_handler(sender, **kwargs):
    return update_active_msisdn(kwargs['instance'])

def update_active_msisdn(patient):
    # only continue if we have a primary key set
    if patient.pk:
        # continue if nothing set as active, but we do have a list of options
        if not patient.active_msisdn and patient.msisdns.count():
            # there is no ordering, depend on the database to specify
            # auto incrementing primary keys
            patient.active_msisdn = patient.msisdns.latest('id')
        
