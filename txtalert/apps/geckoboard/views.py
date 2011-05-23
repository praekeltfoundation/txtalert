from django_geckoboard.decorators import number_widget, line_chart, pie_chart, funnel
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
    visits = Visit.objects.filter(date__gte=week_ago, date__lt=date.today())
    return [
        [visits.filter(status='a').count(), 'Attended', '1D6099'],
        [visits.filter(status='m').count(), 'Missed', 'FF4359'],
        [visits.filter(status='s').count(), 'Scheduled', '239953'],
        [visits.filter(status='r').count(), 'Rescheduled', '992B8B'],
    ]

@number_widget
def visit_attendance(request, status):
    last_month = datetime.now() - timedelta(days=60)
    this_month = datetime.now() - timedelta(days=30)
    visits = Visit.objects.filter(status=status)
    last_months_visits = visits.filter(date__gte=last_month, date__lt=this_month).count()
    this_months_visits = visits.filter(date__gte=this_month, date__lt=datetime.now()).count()
    return (this_months_visits, last_months_visits)

@funnel
def smss_sent_breakdown(request):
    last_month = datetime.now() - timedelta(days=30)
    messages = SendSMS.objects.filter(delivery__gte=last_month)
    return {
        "type": "standard",
        "percentage": "show",
        "items": [
            (messages.count(), "Messages sent"),
            (messages.filter(smstext__startswith='You missed your visit').count(), "Missed message"),
            (messages.filter(smstext__startswith="Thank you for attending").count(), "Attended message"),
            (messages.filter(smstext__startswith="See you at the clinic tomorrow").count(), "Tomorrow reminder"),
            (messages.filter(smstext__startswith="You have an visit at the clinic on").count(), "Two week reminder")
        ],
        "sort": True
    }