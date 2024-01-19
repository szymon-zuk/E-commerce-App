from django.contrib.auth.forms import UserCreationForm
from .models import UserRole


class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for user registration, based on the UserCreationForm.

    This form includes fields from the UserCreationForm and associates the user role.

    Attributes:
    - `model` (UserRole): The user model associated with the form.
    - `fields` (list): The fields to be included in the form.

    Usage Example:
    ```
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
        user = form.save()
    ```

    """

    class Meta(UserCreationForm):
        model = UserRole
        fields = UserCreationForm.Meta.fields
