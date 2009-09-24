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


import threading, time, sys, traceback
from datetime import datetime
from django.core import mail
from cron import cron


class JobBase(type):
    """
    Metaclass for all Jobs.
    """
    def __new__(cls, name, bases, attrs):
        new_class = super(JobBase, cls).__new__(cls, name, bases, attrs)
        parents = [b for b in bases if isinstance(b, JobBase)]
        job_module = sys.modules[new_class.__module__]
        app_label = job_module.__name__.split('.')[-2]
        if parents and not cron.get_job(app_label, name):
            cron.register_job(app_label, new_class)
        return new_class


class Job(threading.Thread):
    __metaclass__ = JobBase

    _param_series = ['minute', 'hour', 'dayofmonth', 'month', 'dayofweek', None]

    _param_format = {
        'minute': '%M',
        'hour': '%H',
        'dayofmonth': '%d',
        'month': '%m',
        'dayofweek': '%w',
    }

    minute, hour, dayofmonth, month, dayofweek = ['*'] * 5

    def now(self, now, name='minute'):
        if name:
            values = getattr(self, name).split(',')
            value = int(now.strftime(self._param_format[name]))
            next_param = self._param_series[self._param_series.index(name)+1]
            for v in values:
                if (v == '*') or (int(v) == value):
                    return self.now(now, next_param)
            return False
        else:
            return True

    def run(self):
        try:
            self.job()
        except:
            import logging
            logging.error("Cron Job Error: %s" % traceback.format_exc())
            mail.mail_admins('Cron Job Error', traceback.format_exc())
    
    def job(self):
        raise NotImplementedError("The 'job' method must be overriden for all classes inheriting from Job.")
