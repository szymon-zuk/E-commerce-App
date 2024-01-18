from rest_framework.permissions import BasePermission


class IsSellerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or (
            request.user.is_authenticated and request.user.userrole.role == "Seller"
        )
