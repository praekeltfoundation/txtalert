from celery import task
from django.core import management


@task
def qa_schedule():
    management.call_command('send_reminders', group='QA Group')


@task
def production_schedule():
    management.call_command('te_import_data', username='kumbu')
    management.call_command('send_reminders', group='Temba Lethu')
    management.call_command('send_reminders', group='wrhi group')
