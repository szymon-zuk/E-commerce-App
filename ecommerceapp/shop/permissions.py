from rest_framework.permissions import BasePermission


class IsSellerOrAdmin(BasePermission):
    """
    Custom permission to only allow seller or superuser to access certain endpoints.
    """

    def has_permission(self, request, view):
        """
        Check if the user is an authenticated seller or superuser.
        """
        return (
            request.user.is_superuser
            or (request.user.is_authenticated and request.user.role == "seller")
            or (request.user.is_authenticated and request.user.role == "admin")
        )
