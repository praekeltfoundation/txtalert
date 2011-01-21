from txtalert.core.utils import MuninCommand
from datetime import date, timedelta
from txtalert.core.models import PleaseCallMe
from txtalert.apps.gateway.models import PleaseCallMe as GatewayPleaseCallMe

class Command(MuninCommand):
    help = "Print out statistics on TherapyEdge, suitable as a Munin plugin"
    
    def config(self):
        self.output({
            'graph_title': 'PCM Statistics',
            'graph_category': 'TxtAlert',
            'graph_vlabel': 'Count',
            'graph_order': 'total linked not_linked',
            'total.label': 'Total amount of PCMs received',
            'linked.label': 'PCMs from known Patient MSISDNs',
            'not_linked.label': 'PCMs from unknown Patient MSISDNs',
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
            'total.value': all_pcms.count(),
            'linked.value': pcms.count(),
            'not_linked.value': all_pcms.count() - pcms.count(),
        })
        