from datetime import date
from txtalert.apps.therapyedge import reminders

def handle(backend, selected_gateway, sms_receipt_handler, group_name):
    # TODO: I'm killing this for now since send_reminders command is still active.
    # today = date.today()
    # reminders.all(selected_gateway, [group_name])
    # reminders.send_stats(selected_gateway, [group_name], today)
    pass
