from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.conf import settings
from txtalert.core.models import (Patient, Clinic, MSISDN, 
                                    VISIT_STATUS_CHOICES, Visit)
from optparse import make_option
from datetime import datetime, timedelta
import random
import sys
from uuid import uuid1

def sample(items):
    return random.sample(items, 1).pop()

PAGES = (
    ('Terms of Service', '/bookings/terms-of-service/', None),
    ('Privacy', '/bookings/privacy/', None),
    ('Terms of Service', '/bookings/admin/terms-of-service/', 'flatpages/admin.html'),
    ('Privacy', '/bookings/admin/privacy/', 'flatpages/admin.html'),
    ('Help', '/bookings/admin/help/', 'flatpages/admin.html'),
    ('Take Our STI Quiz and Win Airtime', '/bookings/young-africa-live/sti-quiz/', None),
    ('More Young Africa Live...', '/bookings/young-africa-live/more/', None),
    ('About txtAlert...', '/bookings/about-txtalert/', None),
)

class Command(BaseCommand):
    help = "Generate flat pages required for txtAlert:bookings"
    def handle(self, *args, **options):
        site = Site.objects.get(pk=settings.SITE_ID)
        for title, url, template in PAGES:
            fp, created = FlatPage.objects.get_or_create(
                url=url,
                title=title,
                template_name=template or ''
            )
            fp.sites.add(site)
            if created:
                print 'Created', title
            if not fp.content:
                fp.content = 'Here comes %s <br/><br/>' \
                    'Lorem ipsum dolor sit amet, consectetur adipisicing elit, '\
                    'sed do eiusmod tempor incididunt ut labore et dolore magna '\
                    'aliqua. Ut enim ad minim veniam, quis nostrud exercitation '\
                    'ullamco laboris nisi ut aliquip ex ea commodo consequat. '\
                    'Duis aute irure dolor in reprehenderit in voluptate velit '\
                    'esse cillum dolore eu fugiat nulla pariatur. Excepteur sint '\
                    'occaecat cupidatat non proident, sunt in culpa qui officia '\
                    'deserunt mollit anim id est laborum.' % title
                fp.save()