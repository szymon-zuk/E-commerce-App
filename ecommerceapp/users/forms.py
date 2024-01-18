from django.contrib.auth.forms import UserCreationForm
from .models import UserRole


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = UserRole
        fields = UserCreationForm.Meta.fields
