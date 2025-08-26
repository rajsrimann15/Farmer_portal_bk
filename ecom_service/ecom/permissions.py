from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class IsTransporter(BasePermission):
    """Allows access only to users with role = transporter."""

    def has_permission(self, request, view):
        role = request.headers.get("X-User-Role")
        if role != "transporter":
            raise PermissionDenied("Only transporters can perform this action")
        return True


class IsConsumer(BasePermission):
    """Allows access only to users with role = consumer."""

    def has_permission(self, request, view):
        role = request.headers.get("X-User-Role")
        if role != "consumer":
            raise PermissionDenied("Only consumers can perform this action")
        return True


class IsFarmer(BasePermission):
    """Allows access only to users with role = farmer."""

    def has_permission(self, request, view):
        role = request.headers.get("X-User-Role")
        if role != "farmer":
            raise PermissionDenied("Only farmers can perform this action")
        return True

class IsWholesaler(BasePermission):
    """Allows access only to users with role = wholesaler."""

    def has_permission(self, request, view):
        role = request.headers.get("X-User-Role")
        if role != "wholesaler":
            raise PermissionDenied("Only wholesalers can perform this action")
        return True

class IsAdmin(BasePermission):
    """Allows access only to users with role = admin."""

    def has_permission(self, request, view):
        role = request.headers.get("X-User-Role")
        if role != "admin":
            raise PermissionDenied("Only admins can perform this action")
        return True