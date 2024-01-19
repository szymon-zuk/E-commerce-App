from allauth.account.signals import user_signed_up
from .models import UserRole
from django.dispatch import receiver

CUSTOMER_ROLE = "customer"


@receiver(user_signed_up)
def set_default_role(sender, user, request, **kwargs):
    """
    Signal receiver to set the default role for a newly registered user.

    This function is connected to the `user_signed_up` signal and automatically
    sets the user's role to the default customer role upon successful registration.

    Parameters:
    - `sender`: The sender of the signal.
    - `user` (UserRole): The newly registered user.
    - `request` (HttpRequest): The HTTP request.
    - `kwargs`: Additional keyword arguments.

    """
    UserRole.objects.filter(pk=user.pk).update(role=CUSTOMER_ROLE)
