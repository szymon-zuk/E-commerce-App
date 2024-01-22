from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import send_mail

logger = get_task_logger(__name__)


@shared_task(name="send-email")
def send_email_task(subject, plain_message, from_email, to_email, html_message=None):
    """
    Celery task to send an email.
    """
    try:
        send_mail(
            subject,
            plain_message,
            from_email,
            to_email,
            html_message=html_message,
        )
        logger.info("Email sent successfully.")
    except Exception as e:
        logger.error(f"Error sending email: {e}")
