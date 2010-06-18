from django.core.management.base import BaseCommand
from django.conf import settings
from django.template import Template
from os.path import join
from core.models import Visit
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = "Print out statistics on TherapyEdge, suitable as a Munin plugin"
    
    def handle(self, *args, **kwargs):
        if args and args[0] == "config":
            return self.config()
        else:
            return self.stats()
    
    def output(self, _dict):
        print "\n".join(["%s %s" % (k,v) for k,v in _dict.items()])
    
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
    
    def stats(self):
        """Print out the stats for Munin"""
        yesterday = datetime.now() - timedelta(days=1)
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
    