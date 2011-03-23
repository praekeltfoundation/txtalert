from django_geckoboard.decorators import number_widget, line_chart
from datetime import datetime, timedelta, date
from txtalert.core.models import Patient
from txtalert.apps.gateway.models import SendSMS

@number_widget
def patient_count(request):
    last_week_start = datetime.now() - timedelta(weeks=2)
    last_week_end = datetime.now() - timedelta(weeks=1)
    patients = Patient.objects
    last_week_patients = patients.filter(
                            created_at__gte=last_week_start,
                            created_at__lte=last_week_end)
    this_week_patients = patients.filter(
                            created_at__gte=last_week_end,
                        )
    return (this_week_patients.count(), last_week_patients.count())


@line_chart
def smss_sent(request):
    since = date.today() - timedelta(days=29)
    days = dict((d, 0) for d in range(0, 29))
    sent_messages = SendSMS.objects.filter(delivery__gte=since)
    for sms in sent_messages:
        days[sms.delivery.date().day] += 1
    return (
        days.values(),
        [days[i] for i in range(1, 29, 7)],
        "SMSs Sent",
    )
    