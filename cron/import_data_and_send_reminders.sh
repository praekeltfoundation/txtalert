#!/bin/bash
cd /var/praekelt/txtalert/production/current/txtalert && \
    source ve/bin/activate && \
        ./manage.py te_import_data --settings=environments.production && \
        ./manage.py te_send_reminders --settings=environments.production && \
    deactivate
