from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class UserRole(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("seller", "Seller"),
        ("customer", "Customer"),
    ]
    role = models.CharField(choices=ROLE_CHOICES, max_length=20)

    def __str__(self):
        return f"{self.username} - {self.role}"
