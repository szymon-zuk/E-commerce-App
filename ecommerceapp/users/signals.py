from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.models import EmailConfirmation
from allauth.account.signals import user_signed_up
from .models import UserRole


@receiver(user_signed_up)
def set_default_role(sender, user, request, **kwargs):
    user.role = "customer"
    user.save()
