from django_geckoboard.decorators import number_widget, line_chart, pie_chart
from datetime import datetime, timedelta, date
from txtalert.core.models import Patient, PleaseCallMe, Visit
from txtalert.apps.gateway.models import SendSMS

@number_widget
def patient_count(request):
    last_week_start = datetime.now() - timedelta(weeks=2)
    last_week_end = datetime.now() - timedelta(weeks=1)
    patients = Patient.objects
    last_week_patients = patients.filter(
                            created_at__gte=last_week_start,
                            created_at__lt=last_week_end)
    this_week_patients = patients.filter(
                            created_at__gte=last_week_end,
                        )
    return (this_week_patients.count(), last_week_patients.count())


@number_widget
def smss_sent(request):
    last_week_start = datetime.now() - timedelta(weeks=2)
    last_week_end = datetime.now() - timedelta(weeks=1)
    smss = SendSMS.objects
    last_week_sms = smss.filter(
                            delivery__gte=last_week_start,
                            delivery__lt=last_week_end)
    this_week_sms = smss.filter(
                            delivery__gte=last_week_end,
                        )
    return (this_week_sms.count(), last_week_sms.count())

@number_widget
def pcms_received(request):
    last_week_start = datetime.now() - timedelta(weeks=2)
    last_week_end = datetime.now() - timedelta(weeks=1)
    pcms = PleaseCallMe.objects
    last_week_pcms = pcms.filter(
                            timestamp__gte=last_week_start,
                            timestamp__lt=last_week_end)
    this_week_pcms = pcms.filter(
                            timestamp__gte=last_week_end,
                        )
    return (this_week_pcms.count(), last_week_pcms.count())

@pie_chart
def visit_status(request):
    week_ago = datetime.now() - timedelta(weeks=1)
    visits = Visit.objects.filter(date__gte=week_ago)
    return [
        [visits.filter(status='a').count(), 'Attended'],
        [visits.filter(status='m').count(), 'Missed'],
        [visits.filter(status='s').count(), 'Scheduled'],
        [visits.filter(status='r').count(), 'Rescheduled'],
    ]