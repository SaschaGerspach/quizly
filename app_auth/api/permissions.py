from django.conf import settings
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


class IsAnonymousOnly(BasePermission):
    """
    Allow access only to unauthenticated users.
    Useful for register/login endpoints.
    """

    def has_permission(self, request, view) -> bool:
        return not request.user or not request.user.is_authenticated
    
class RequiresValidRefreshCookie(BasePermission):
    """
    Allow only if a valid refresh token cookie is present.
    Spec: Authentication via `refresh_token` cookie required.
    """

    message = "Refresh token is missing or invalid."

    def has_permission(self, request, view) -> bool:
        cookie_name = getattr(settings, "REFRESH_COOKIE", "refresh_token")
        raw_refresh = request.COOKIES.get(cookie_name)
        if not raw_refresh:
            return False
        try:
            # Validate token structure/signature/expiry
            RefreshToken(raw_refresh)
            return True
        except TokenError:
            return False
    


