from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Configuration class for the 'users' app.

    This class defines the app's configuration, including the default auto field
    and any actions to be performed when the app is ready.

    Attributes:
    - `default_auto_field` (str): The default auto field for model primary keys.
    - `name` (str): The name of the app.

    Methods:
    - `ready()`: Action to be performed when the app is ready."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        """
        Action to be performed when the app is ready.

        This method imports the 'users.signals' module to ensure that signal
        receivers are connected when the app is ready."""
        import users.signals
