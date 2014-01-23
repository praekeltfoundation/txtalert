#!/bin/bash
cd /var/praekelt/txtalert && \
    source ve/bin/activate && \
        ./manage.py te_import_data --settings=production_settings --user='kumbu' | mail -s "TxtAlert TE import on `date`" dev@praekeltfoundation.org && \
        ./manage.py send_reminders --settings=production_settings --group='Temba Lethu' | mail -s "TxtAlert TE reminders for Temba Lethu on `date`" dev@praekeltfoundation.org && \
        python -W"ignore" ./manage.py gd_import_data --settings=production_settings 2>&1 | mail -s "TxtAlert Google Docs import on `date`" txtalert-wrhi@praekeltfoundation.org && \
        ./manage.py send_reminders --settings=production_settings --group='wrhi group' | mail -s "TxtAlert GD reminders for WrHI Group on `date`" dev@praekeltfoundation.org && \
    deactivate
