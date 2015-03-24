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


@task
def wrhi_qa_schedule():
    management.call_command('import_wrhi_data', endpoint='qa_txtalert_api')


@task
def wrhi_prod_schedule():
    management.call_command('import_wrhi_data', endpoint='prod_txtalert_api')