from core.utils import MuninCommand
from datetime import date, timedelta
from core.models import PleaseCallMe
from gateway.models import PleaseCallMe as GatewayPleaseCallMe

class Command(MuninCommand):
    help = "Print out statistics on TherapyEdge, suitable as a Munin plugin"
    
    def config(self):
        self.output({
            'graph_title': 'PCM Statistics',
            'graph_category': 'TxtAlert',
            'graph_vlabel': 'Count',
            'graph_order': 'received not_linked',
            'received.label': 'PCMs received',
            'not_linked.label': 'PCMs from unknown Patient MSISDN',
        })
    
    def run(self):
        today = date.today()
        pcms = PleaseCallMe.objects.filter(timestamp__day=today.day,
                                            timestamp__month=today.month,
                                            timestamp__year=today.year)
        all_pcms = GatewayPleaseCallMe.objects.filter(
                                                created_at__day=today.day,
                                                created_at__month=today.month,
                                                created_at__year=today.year)
        self.output({
            'received.value': pcms.count(),
            'not_linked.value': all_pcms.count() - pcms.count(),
        })
        