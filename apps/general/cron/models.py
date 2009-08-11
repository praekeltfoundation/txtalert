# Copyright (c) 2009, Jurie-Jan Botha
#
# This file is part of the 'cron' Django application.
#
# 'cron' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# 'cron' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with the 'cron' application. If not, see
# <http://www.gnu.org/licenses/>.


from django.db import models


class Job(models.Model):
    _param_series = {
        'minute': 'hour',
        'hour': 'day_of_month',
        'day_of_month': 'month',
        'month': 'day_of_week',
        'day_of_week': None,
    }

    _param_format = {
        'minute': '%M',
        'hour': '%H',
        'day_of_month': '%d',
        'month': '%m',
        'day_of_week': '%w',
    }

    function_name = models.CharField('Function Name', max_length=255)
    minute = models.SmallIntegerField('Minute', default='*')
    hour = models.SmallIntegerField('Hour', default='*')
    day_of_month = models.SmallIntegerField('Day Of Month', default='*')
    month = models.SmallIntegerField('Month', default='*')
    day_of_week = models.SmallIntegerField('Day Of Week', default='*')

    class Meta:
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'

    def __unicode__(self):
        return "%s (%s %s %s %s %s)" % (self.function_name, self.minute, self.hour, self.day_of_month, self.month, self.day_of_week)

    def isNow(self, now, name='minute'):
        if name:
            values = getattr(self, name)
            value = int(now.strftime(self._param_format[name]))
            next_param = self._param_series[name]
            for v in values:
                if (v == '*') or (int(v) == value):
                    return self.isNow(now, next_param)
            return False
        else:
            self._now = now
            return True

    def start(self):
        exec("thread = threading.Thread(target=%s)" % self.function_name)
        thread.start()
