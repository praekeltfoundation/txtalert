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


import threading, time, os, sys, traceback
from datetime import datetime

from django.core import mail
from django.utils.datastructures import SortedDict


class CronThread(threading.Thread):
    stopevent = threading.Event()

    def __init__(self, cron):
        super(CronThread, self).__init__()
        self.cron = cron
        self.setDaemon(True)

    def run(self):
        while not self.stopevent.isSet():
            now = datetime.now()
            delta = 60 - (now.second % 60)
            time.sleep(delta)
            now = datetime.now()

            for app in self.cron.app_jobs.values():
                for job_class in app.values():
                    job = job_class()
                    if job.now(now):
                        job.start()


class Cron(object):
    """
    Stores jobs to be run at indicated times.
    """

    __shared_state = dict(
        app_jobs = SortedDict(),
        thread = None,
    )

    def __init__(self, *args, **kwargs):
        self.__dict__ = self.__shared_state

    def get_job(self, app_label, job_name):
        """
        Returns the job matching the given app_label and case-insensitve
        job_name.

        Returns None if no job is found.
        """
        return self.app_jobs.get(app_label, SortedDict()).get(job_name.lower())

    def register_job(self, app_label, *jobs):
        """
        Register a set of jobs belonging to an application.
        """
        for job in jobs:
            job_name = job.__name__.lower()
            job_dict = self.app_jobs.setdefault(app_label, SortedDict())
            if job_name in job_dict:
                # The same job may be imported via different paths (e.g.
                # appname.jobs and project.appname.jobs). We use the source
                # filename as a means to detect identity.
                fname1 = os.path.abspath(sys.modules[job.__module__].__file__)
                fname2 = os.path.abspath(sys.modules[job_dict[job_name].__module__].__file__)
                # Since the filename extension could be .py the first time and
                # .pyc or .pyo the second time, ignore the extension when
                # comparing.
                if os.path.splitext(fname1)[0] == os.path.splitext(fname2)[0]:
                    continue
            job_dict[job_name] = job

    def start(self):
        if self.thread: self.thread.stop()
        self.thread = CronThread(self)
        self.thread.start()

    def stop(self):
        self.thread.stopevent.set()


cron = Cron()
