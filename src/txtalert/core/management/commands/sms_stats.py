from txtalert.core.utils import MuninCommand
from datetime import date, timedelta
from txtalert.apps.gateway.models import SendSMS

class Command(MuninCommand):
    help = "Print out statistics on TherapyEdge, suitable as a Munin plugin"
    
    def config(self):
        self.output({
            'graph_title': 'SMS Statistics',
            'graph_category': 'TxtAlert',
            'graph_vlabel': 'Count',
            'graph_order': 'total delivered',
            'total.label': 'SMSs Sent',
            'delivered.label': 'SMSs that have been delivered successfully',
        })
    
    def run(self):
        today = date.today()
        sms = SendSMS.objects.filter(delivery__day=today.day,
                                        delivery__month=today.month,
                                        delivery__year=today.year)
        self.output({
            'total.value': sms.count(),
            'delivered.value': sms.filter(status='D').count(),
        })
