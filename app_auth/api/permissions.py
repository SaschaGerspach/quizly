from rest_framework.permissions import BasePermission


class IsAnonymousOnly(BasePermission):
    """
    Allow access only to unauthenticated users.
    Useful for register/login endpoints.
    """

    def has_permission(self, request, view) -> bool:
        return not request.user or not request.user.is_authenticated
