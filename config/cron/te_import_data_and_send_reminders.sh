#!/bin/bash
cd /var/praekelt/txtalert/production/current/txtalert && \
    source ve/bin/activate && \
        ./manage.py te_import_data --settings=environments.production | mail -s "TxtAlert TE import on `date`" dev@praekeltfoundation.org && \
        ./manage.py send_reminders --settings=environments.production --group='Temba Lethu' | mail -s "TxtAlert TE reminders for Temba Lethu on `date`" dev@praekeltfoundation.org && \
    deactivate
