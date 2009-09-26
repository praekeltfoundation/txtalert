from django.core.management.base import BaseCommand
from django.conf import settings
from general.settings.models import Setting
from therapyedge import reminders
from datetime import datetime

class Command(BaseCommand):
    help = "Can be run as a cronjob or directly to send SMS reminders."
    def handle(self, *args, **kwargs):
        gateway = Setting.objects.get(name='Gateway').value
        today = datetime.now().date()
        reminders.all(gateway)
        reminders.send_stats(gateway, today)
        