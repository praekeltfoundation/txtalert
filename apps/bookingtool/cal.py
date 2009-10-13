# http://journal.uggedal.com/creating-a-flexible-monthly-calendar-in-django
from calendar import HTMLCalendar
from datetime import date
from itertools import groupby

from django.utils.html import conditional_escape as esc
from django.conf import settings

from models import Visit

def risk_for_visit_count(visit_count):
    for level, check in settings.BOOKING_TOOL_RISK_LEVELS.items():
        if check(visit_count):
            return level

def risk_on_date(_date):
    visit_count = Visit.objects.filter(date__exact=_date).count()
    return risk_for_visit_count(visit_count)


class RiskCalendar(HTMLCalendar):
    
    def __init__(self, visits):
        super(RiskCalendar, self).__init__()
        self.visits = self.group_by_day(visits)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
            if day in self.visits:
                risk = risk_for_visit_count(len(self.visits[day]))
                cssclass += ' %s' % risk
            return self.day_cell(cssclass, day)
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(RiskCalendar, self).formatmonth(year, month)

    def group_by_day(self, all_visits):
        field = lambda visit: visit.date.day
        return dict(
            [(day, list(visits_on_day)) for day, visits_on_day 
                                                in groupby(all_visits, field)]
        )

    def day_cell(self, cssclass, body):
        return """<td class="day %s">
                    <a href="#">%s</a>
                </td>""" % (cssclass, body)