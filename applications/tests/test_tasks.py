from django.test import TestCase
from django.core import mail
from applications.tasks import send_application_email_task

class CeleryTaskTest(TestCase):
    def test_send_application_email_task(self):
        # Call the task synchronously
        send_application_email_task("test@example.com", "Job Application", "Hello, test message")

        # Django stores test emails in mail.outbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Job Application")
        self.assertEqual(mail.outbox[0].to, ["test@example.com"])
        self.assertIn("Hello, test message", mail.outbox[0].body)
