#  This file is part of TxtAlert.
#
#  TxtALert is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TxtAlert is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with TxtAlert.  If not, see <http://www.gnu.org/licenses/>.


import re, errno, socket, time
from xmlrpclib import ServerProxy, Error, ProtocolError
from datetime import datetime, timedelta, date
import logging

from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from events import ImportEvent, ImportEvents

import models


import logging
logger = logging.getLogger("importing")

SERVICE_URL = 'https://196.36.218.99/tools/ws/sms/patients/server.php'

PATIENT_ID_RE = re.compile(r'^[0-9]{2}-[0-9]{5}$')
PATIENT_AGE_RE = re.compile(r'^[0-9]{1,3}$')
PATIENT_SEX_RE = re.compile(r'^(Male|Female|Transgender ?(f->m|m->f)?)$')

APPOINTMENT_ID_RE = re.compile(r'^[0-9]{2}-[0-9]{9}$')
DATE_RE = re.compile(r'^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{2}:[0-9]{2}:[0-9]{2}$')

MSISDNS_RE = re.compile(r'^([+]?(0|27)[0-9]{9}/?)+$')
MSISDN_RE = re.compile(r'[+]?(0|27)([0-9]{9})')

IMPORT_CUTOFF = datetime(2009, 01, 01)
IMPORT_DAY_INTERVAL = 10

MESSAGE_PATIENTID_INCONSISTENT = "Patient ID '%s' is inconsistent with previous ID '%s' for visit '%s'."
MESSAGE_PATIENT_NOTFOUND = "Patient with the ID '%s' could not be found for visit '%s'."
MESSAGE_VISIT_NOTFOUND = "Visit with the ID '%s' could not be found."


class ImportError(Exception):
    pass


def importRanges(content_type, clinic, days_ahead=0):
    import_events = models.ImportEvent.objects.filter(
        content_type=content_type, clinic=clinic
    ).order_by('-stamp')
    if len(import_events) < 1:
        start = IMPORT_CUTOFF
    else:
        start = import_events[0].stamp
    end = datetime.now() + timedelta(days=days_ahead)
    
    # split the period into intervals
    ranges = []
    if start != end:
        prev = start 
        delta = end - start
        for n in range(IMPORT_DAY_INTERVAL, delta.days)[::IMPORT_DAY_INTERVAL]:
            next = start + timedelta(n)
            ranges.append({'start':str(prev)[:10], 'end':str(end)[:10]})
            prev = next
        ranges.append({'start':str(prev)[:10], 'end':str(end)[:10]})
    
    return ranges


def validateField(event, record, regex, key, name):
    value = None
    try:
        value = record[key]
        if not regex.match(value):
            event.append("Record %s has an invalid value '%s' for the '%s' property." % (record, value, name), 'error')
    except KeyError:
        event.append("Record %s is missing the '%s' property." % (record, name), 'error')
    return value


def importRecords(server, events, clinic, ranges, request, action):
    for range in ranges:
        logger.debug("Getting range '%s' for clinic '%s' with action '%s'" % (range, clinic, action))
        
        # FIXME: very fragile
        # loop the server communication to avoid being held up by errors
        while True:
            try:
                records = server.patients_data(request, 0, range['start'], range['end'], 3, clinic.te_id)
                break
            except socket.error, err:
                logger.error(err)
                if not (err[0] in (errno.ETIMEDOUT, errno.ECONNRESET, 8)): 
                    raise err
            except ProtocolError, err:
                logger.error("A protocol error occurred")
                logger.error("URL: %s" % err.url)
                logger.error("HTTP/HTTPS headers: %s" % err.headers)
                logger.error("Error code: %d" % err.errcode)
                logger.error("Error message: %s" % err.errmsg)
                raise err
        
        for record in records:
            event = ImportEvent()
            try:
                logger.debug("Calling '%s' with args '%s'" % (action, (event, clinic, record)))
                event = action(event, clinic, record)
            except ImportError, e:
                logger.error(e)
                event.append(str(e), 'error')
            events.append(event)
    return events
    

def importPatient(event, clinic, record):
    te_id = validateField(event, record, PATIENT_ID_RE, 'te_id', 'Patient ID')
    age = validateField(event, record, PATIENT_AGE_RE, 'age', 'Age')
    sex = validateField(event, record, PATIENT_SEX_RE, 'sex', 'Sex')
    msisdns = validateField(event, record, MSISDNS_RE, 'celphone', 'Mobile Number')
    
    if event.isError():
        logger.error("Event Error: %s" % event.messages)
    else:
        try:
            patient = models.Patient.objects.get(te_id=te_id)
            event.append("Updated patient record for id '%s'." % (te_id), 'update')
        except ObjectDoesNotExist:
            patient = models.Patient(te_id=te_id)
            event.append("Created new patient record for id '%s'." % (te_id), 'new')
        patient.age = age
        patient.sex = (
            'm' if sex == 'Male' \
            else 'f' if sex == 'Female' \
            else 'f>m' if sex == 'Transgender f->m' \
            else 'm>f' if sex == 'Transgender m->f' \
            else 't'
        )
        patient.save()
        patient.msisdns.clear()
        for msisdn in msisdns.split('/'):
            msisdn = '27' + MSISDN_RE.match(msisdn).groups()[1]
            try:
                msisdn = models.MSISDN.objects.get(msisdn=msisdn)
            except ObjectDoesNotExist:
                msisdn = models.MSISDN(msisdn=msisdn)
            msisdn.save()
            patient.msisdns.add(msisdn)
        patient.save()
    
    return event


def importPatients():
    ct = models.ContentType.objects.get(model='patient')
    server = ServerProxy(SERVICE_URL, verbose=settings.DEBUG)
    all_events = ImportEvents()
    
    if models.Patient.objects.count() == 0:
        # import all patient data
        for clinic in models.Clinic.objects.all():
            events = ImportEvents()
            events = importRecords(server, events, clinic, [{'start':'', 'end':''}], 'patientlist', importPatient)
            models.ImportEvent.objects.create(content_type=ct, clinic=clinic, events=events)
            all_events.extend(events)
    else:
        # update patient data
        for clinic in models.Clinic.objects.all():
            events = ImportEvents()
            events = importVisitData(server, events, clinic, importRanges(ct, clinic, 0), 'patients_update', importPatient)
            models.ImportEvent.objects.create(content_type=ct, clinic=clinic, events=events)
            all_events.extend(events)
    
    return all_events


def getPatient(patient_id, visit_id):
    try:
        return models.Patient.objects.get(te_id=patient_id)
    except ObjectDoesNotExist:
        raise ImportError(MESSAGE_PATIENT_NOTFOUND % (patient_id, visit_id))


def getVisit(visit_id):
    try:
        return models.Visit.objects.get(te_visit_id=visit_id)
    except ObjectDoesNotExist:
        raise ImportError(MESSAGE_VISIT_NOTFOUND % (visit_id))


def validateVisitRecord(event, record):
    date_key = (set(record.keys()) & set(['scheduled_visit_date', 'done_date', 'missed_date'])).pop()
    
    visit_id = validateField(event, record, APPOINTMENT_ID_RE, 'key_id', 'Visit ID')
    patient_id = validateField(event, record, PATIENT_ID_RE, 'te_id', 'Patient ID')
    date = validateField(event, record, DATE_RE, date_key, 'Date')
    try: date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()
    except ValueError: pass
    
    return event, visit_id, patient_id, date 


def importVisitData(server, events, clinic, ranges, request, action):
    for range in ranges:
        # loop the server communication to avoid being held up by errors
        while True:
            try:
                print clinic.te_id
                records = server.patients_data(request, 0, range['start'], range['end'], 3, clinic.te_id)
                break
            except socket.error, e:
                if not e[0] == errno.ECONNRESET: raise e
            
        for record in records:
            event = ImportEvent()
            try:
                event = action(event, clinic, record)
            except ImportError, e:
                event.append(str(e), 'error')
            events.append(event)
    return events
    

def importComingVisit(event, clinic, record):
    event, visit_id, patient_id, date = validateVisitRecord(event, record)
    if not event.isError():
        patient = getPatient(patient_id, visit_id)
        try:
            visit = models.Visit.objects.get(te_visit_id=visit_id)
            if visit.date != date:
                visit.date = date
                visit.status = 's'
                visit.save()
                event.append("Visit '%s' had it's scheduled date updated." % (visit_id), 'update')
        except ObjectDoesNotExist:
            visit = models.Visit.objects.create(te_visit_id=visit_id, 
                                                clinic=clinic, 
                                                patient=patient, 
                                                date=date,
                                                status='s')
            event.append("New visit with id '%s' created." % (visit_id), 'new')
    return event


def importMissedVisit(event, clinic, record):
    event, visit_id, patient_id, date = validateVisitRecord(event, record)
    if not event.isError() or not (date > datetime.now().date()):
        patient = getPatient(patient_id, visit_id)
        try:
            visit = models.Visit.objects.get(te_visit_id=visit_id)
            # if the new date is earlier than the existing date treat it as a 
            # reschedule, otherwise a missed visit
            visit.status = ('r' if date < visit.date else 'm') 
            visit.date = date
            visit.save()
            
            event.append("Visit '%s' had it's status updated." % (visit_id), 'update')
        except ObjectDoesNotExist:
            visit = models.Visit.objects.create(te_visit_id=visit_id, 
                                                clinic=clinic, 
                                                patient=patient, 
                                                date=date,
                                                status='m'
                                            )
            event.append("New visit with id '%s' created." % (visit_id), 'new')
    return event


def importDoneVisit(event, clinic, record):
    event, visit_id, patient_id, date = validateVisitRecord(event, record)
    if not event.isError():
        patient = getPatient(patient_id, visit_id)
        try:
            visit = models.Visit.objects.get(te_visit_id=visit_id)
            visit.date = date
            visit.status = 'a'
            visit.save()
            
            event.append("Visit '%s' was updated." % (visit_id), 'update')
        except ObjectDoesNotExist:
            visit = models.Visit.objects.create(te_visit_id=visit_id, 
                                                clinic=clinic, 
                                                patient=patient, 
                                                date=date,
                                                status='a')
            event.append("New visit with id '%s' created." % (visit_id), 'new')
    return event


def importDeletedVisit(event, clinic, record):
    visit_id = validateField(event, record, APPOINTMENT_ID_RE, 'key_id', 'Visit ID')
    patient_id = validateField(event, record, PATIENT_ID_RE, 'te_id', 'Patient ID')
    if not event.isError():
        try:
            visit = models.Visit.objects.get(te_visit_id=visit_id)
            visit.delete()
            event.append("Deleted visit with id '%s'." % (visit_id), 'update')
        except ObjectDoesNotExist:
            event.append(MESSAGE_VISIT_NOTFOUND % (visit_id), 'error')
    return event
    

def importVisits():
    ct = models.ContentType.objects.get(model='visit')
    server = ServerProxy(SERVICE_URL)
    all_events = ImportEvents()
    
    for clinic in models.Clinic.objects.all():
        events = ImportEvents()
        events = importRecords(server, events, clinic, importRanges(ct, clinic, 31), 'comingvisits', importComingVisit)
        events = importRecords(server, events, clinic, importRanges(ct, clinic), 'missedvisits', importMissedVisit)
        events = importRecords(server, events, clinic, importRanges(ct, clinic), 'donevisits', importDoneVisit)
        events = importRecords(server, events, clinic, importRanges(ct, clinic), 'deletedvisits', importDeletedVisit)
        models.ImportEvent.objects.create(content_type=ct, clinic=clinic, events=events)
        all_events.extend(events)
    
    return all_events


def importAll():
    logger.debug("importing patients")
    events = importPatients()
    message = "New: %s\nUpdated: %s\nErrors: %s\n\n%s" % (events.new, events.updated, events.errors, '\n'.join(events.error_messages)) 
    logger.debug("mailing admins: %s" % message)
    mail.mail_admins('Patient Import Report', message, fail_silently=True)
    
    logger.debug("importing visits")
    events = importVisits()
    message = "New: %s\nUpdated: %s\nErrors: %s\n\n%s" % (events.new, events.updated, events.errors, '\n'.join(events.error_messages)) 
    logger.debug("mailing admings: %s" % message)
    mail.mail_admins('Visit Import Report', message, fail_silently=True)
