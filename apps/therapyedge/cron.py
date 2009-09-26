#  This file is part of TxtAlert.
#
#  TxtALert is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TxtAlert is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with TxtAlert.  If not, see <http://www.gnu.org/licenses/>.


from datetime import datetime
from general.cron import Job
from general.settings.models import Setting
from therapyedge import reminders, importing


class SendReminders(Job):
    hour, minute = '09', '00'

    def job(self):
        gateway = Setting.objects.get(name='Gateway').value
        today = datetime.now().date()
        reminders.all(gateway)
        reminders.send_stats(gateway, today)


class ImportJob(Job):
    hour, minute = '08', '00'

    def job(self):
        importing.importAll()
