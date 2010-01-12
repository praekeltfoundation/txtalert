from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
# from therapyedge import importing

class Command(BaseCommand):
    help = "Can be run as a cronjob or directly to send import TherapyEdge data."
    def handle(self, *args, **kwargs):
        importing.importAll()