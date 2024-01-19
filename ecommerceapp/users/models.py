from django.db import models
from django.contrib.auth.models import AbstractUser


class UserRole(AbstractUser):
    """
    Custom user model that extends regular auth_user with one field: `role`.
    Permissions in endpoints are based on user roles.
    """

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("seller", "Seller"),
        ("customer", "Customer"),
    ]
    role = models.CharField(choices=ROLE_CHOICES, max_length=20)

    def __str__(self):
        return f"{self.username} - {self.role}"
