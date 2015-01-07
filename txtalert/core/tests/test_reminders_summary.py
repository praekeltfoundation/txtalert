from uuid import uuid4
from StringIO import StringIO
from django.contrib.auth.models import User, Group
from django.utils import timezone

from txtalert.core.models import Clinic, MessageType, Language
from txtalert.core.tests.base import BaseTxtAlertTestCase
from txtalert.core.management.commands import reminders_summary


class TestRemindersSummary(BaseTxtAlertTestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            'admin', 'admin@admin.com', password='admin')

        self.clinic1_group = Group.objects.create(name='clinic group 1')
        self.clinic1_user = User.objects.create_user(
            'clinic1', 'clinic1@clinic1.com', password='clinic1')
        self.clinic1_user.groups = [self.clinic1_group]
        self.clinic1_user.save()

        self.clinic1 = Clinic.objects.create(
            name='Clinic 1', user=self.clinic1_user, te_id=uuid4().hex)

        self.clinic2_group = Group.objects.create(name='clinic group 2')
        self.clinic2_user = User.objects.create_user(
            'clinic2', 'clinic2@clinic2.com', password='clinic2')
        self.clinic2_user.groups = [self.clinic2_group]
        self.clinic2_user.save()

        self.clinic2 = Clinic.objects.create(
            name='Clinic 2', user=self.clinic2_user, te_id=uuid4().hex)

        message_pairs = [
            ('twoweeks_message', 'Come in two weeks'),
            ('tomorrow_message', 'Come tomorrow'),
            ('attended_message', 'Thanks for attending'),
            ('missed_message', 'You missed your appointment'),
        ]
        for name, message in message_pairs:
            MessageType.objects.create(
                group=self.clinic1_group,
                clinic=self.clinic1,
                language=Language.objects.get(name='English'),
                name=name,
                message=message)

    def test_reminders_summary(self):

        from txtalert.apps.gateway.backends.debug.backend import Gateway
        original_stdout, Gateway.stdout = Gateway.stdout, StringIO()

        [patient] = self.create_patients(self.clinic1, count=1)
        self.create_missed_visit(patient, self.clinic1)
        self.create_twoweek_visit(patient, self.clinic1)
        command = reminders_summary.Command()
        command.handle(group=self.clinic1_group.name,
                       date=timezone.now().strftime(command.DATE_FORMAT))
        expected_output = [
            "Sending 'Come tomorrow' to '27000000000' from 'clinic1'",
            "Sending 'Come in two weeks' to '27000000000' from 'clinic1'",
            "Sending 'Thanks for attending' to '27000000000' from 'clinic1'",
            ("Sending 'You missed your appointment' to '27000000000' from "
             "'clinic1'"),
        ]
        self.assertEqual(
            Gateway.stdout.getvalue().strip(),
            '\n'.join(expected_output).strip())

        Gateway.stdout = original_stdout
