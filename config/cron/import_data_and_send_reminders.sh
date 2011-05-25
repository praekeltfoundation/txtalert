#!/bin/bash
cd /var/praekelt/txtalert/production/current/txtalert && \
    source ve/bin/activate && \
        ./manage.py te_import_data --settings=environments.production | mail -s "TxtAlert TE import on `date`" dev@praekeltfoundation.org && \
        ./manage.py te_send_reminders --settings=environments.production | mail -s "TxtAlert TE reminders on `date`" dev@praekeltfoundation.org && \
    deactivate
