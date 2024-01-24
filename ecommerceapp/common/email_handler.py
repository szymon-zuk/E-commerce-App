from django.conf import settings
from shop.models import Order
from shop.tasks import send_email_task
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone


class EmailHandler:
    from_email = settings.EMAIL_HOST_USER

    @classmethod
    def send_confirmation_email(cls, to_email: list, order: Order):
        """
        Send an order confirmation email to the user using Celery task.

        Parameters:
        - `order` (Order): The order instance.
        - `to_email` (str): The email address of the recipient

        Returns:
        - None
        """
        subject = "Order Confirmation"
        html_message = render_to_string("confirmation_email.html", {"order": order})
        plain_message = strip_tags(html_message)

        send_email_task.delay(
            subject,
            plain_message,
            cls.from_email,
            [to_email],
            html_message=html_message,
        )

    @classmethod
    def send_payment_reminder_email(cls, to_email: str, order: Order):
        """
        Send a payment reminder email to the user using Celery task.

        Parameters:
        - `order` (Order): The order instance.
        - `to_email` (str): The email address of the recipient

        Returns:
        - None
        """
        subject = "Payment reminder"
        html_message = render_to_string("payment_reminder_email.html", {"order": order})
        plain_message = strip_tags(html_message)

        send_email_task.apply_async(
            args=(subject, plain_message, cls.from_email, [to_email]),
            kwargs={"html_message": html_message},
            eta=order.payment_due_date - timezone.timedelta(days=1),
        )
