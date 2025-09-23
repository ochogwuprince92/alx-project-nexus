from django.core.mail import send_mail
from django.conf import settings

def send_application_email(to_email, subject, message):
    """
    Utility function to send email notifications for job applications.
    """
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # From
        [to_email],               # Recipient
        fail_silently=False,
    )
