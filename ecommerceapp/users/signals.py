from allauth.account.signals import user_signed_up
from .models import UserRole
from django.dispatch import receiver

CUSTOMER_ROLE = "customer"


@receiver(user_signed_up)
def set_default_role(sender, user, request, **kwargs):
    UserRole.objects.filter(pk=user.pk).update(role=CUSTOMER_ROLE)
