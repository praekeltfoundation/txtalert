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
    sent_messages = SendSMS.objects
    weeks = {}
    week_range = range(0,4)
    for week in week_range:
        start = datetime.now() - timedelta(weeks=week+1)
        end = datetime.now() - timedelta(weeks=week)
        weeks[week] = SendSMS.objects.filter(delivery__gte=start, delivery__lt=end).count()
    return (
        [weeks[i] for i in week_range],
        ["%i Weeks ago" % (i + 1,) for i in week_range],
        "SMSs sent per week"
    )