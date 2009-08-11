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


import os, sys, time

from django.core.management import setup_environ
from txtalert import settings
from general.cron.models import Job
from cron import cron

setup_environ(settings)


def auto_discover():
    """
    Auto-discover INSTALLED_APPS cron.py modules and fail silently when
    not present. This forces an import on them to register any cron jobs they
    may want.
    """
    import imp
    import inspect
    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        try:
            app_path = __import__(app, {}, {}, [app.split('.')[-1]]).__path__
        except AttributeError:
            continue

        try:
            imp.find_module('cron', app_path)
        except ImportError:
            continue

        module = __import__("%s.cron" % app_path)
        
        for name in dir(module):
            obj = getattr(module, name)
            if inspect.isclass(obj) and isinstance(obj, Job):
                cron.add(obj)
                

if __name__ == '__main__':
    print dir(settings)


"""
while 1:
    now = datetime.now()
    delta = 60 - (now.second % 60)
    time.sleep(delta)

    for job in Job.objects.all():
        if job.isNow(now):
            job.start()
"""

"""
if __name__ == '__main__':
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.exit(1)

    os.chdir("/")
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.exit(1)

    main()
"""
