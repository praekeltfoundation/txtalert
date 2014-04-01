#!/bin/bash
cd /var/praekelt/txtalert && \
    source ve/bin/activate && \
        ./manage.py te_import_data --user='kumbu' | mail -s "TxtAlert TE import on `date`" simon@praekeltfoundation.org && \
        ./manage.py send_reminders --group='Temba Lethu' | mail -s "TxtAlert TE reminders for Temba Lethu on `date`" simon@praekeltfoundation.org && \
        ./manage.py send_reminders --group='wrhi group' | mail -s "TxtAlert GD reminders for WrHI Group on `date`" simon@praekeltfoundation.org && \
    deactivate
