from django.conf import settings
from os.path import join
from txtalert.core.models import Visit
from datetime import date, timedelta
from txtalert.core.utils import MuninCommand

class Command(MuninCommand):
    help = "Print out statistics on TherapyEdge, suitable as a Munin plugin"
    
    def config(self):
        """Print out the plugin configuration for Munin"""
        self.output({
            'graph_title': 'TherapyEdge Statistics',
            'graph_category': 'TxtAlert',
            'graph_vlabel': 'Count',
            'graph_order': 'attended missed percentage',
            'attended.label': 'Attended',
            'missed.label': 'Missed',
            'percentage.label': 'Percentage Missed'
        })
    
    def run(self):
        """Print out the stats for Munin"""
        yesterday = date.today() - timedelta(days=1)
        visits = Visit.objects.filter(patient__opted_in=True)
        attended_count = visits.filter(status__exact='a',
                                        date__exact=yesterday).count()
        missed_count = visits.filter(status__exact='m', 
                                        date__exact=yesterday).count()
        yesterday_count = missed_count + attended_count
        if yesterday_count == 0: missed_percentage = 0
        else: missed_percentage = missed_count * (100.0 / yesterday_count)
        
        self.output({
            'attended.value': attended_count,
            'missed.value': missed_count,
            'percentage.value': '%.1f' % missed_percentage
        })
    