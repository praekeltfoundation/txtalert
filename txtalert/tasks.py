from celery import task
from django.core import management


@task
def qa_schedule():
    management.call_command('send_reminders', group='QA Group')


# NOTE: this is not in use yet, production still uses cron
#
# @task
# def production_schedule():
#     management.call_command('te_import_data', user='kumbu')
#     management.call_command('send_reminders', group='Temba Lethu')
#     management.call_command('send_reminders', group='wrhi group')
