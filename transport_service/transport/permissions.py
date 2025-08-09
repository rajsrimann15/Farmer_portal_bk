from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class IsTransporter(BasePermission):
    """
    Allows access only to users with role = transporter.
    """

    def has_permission(self, request, view):
        role = request.headers.get("X-User-Role")
        if role != "transporter":
            raise PermissionDenied("Only transporters can perform this action")
        return True
