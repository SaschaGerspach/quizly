from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    """
    Authenticate via Authorization header first; if absent, fall back to JWT in HttpOnly cookie.
    Cookie name is taken from settings.AUTH_COOKIE (default: "access_token").
    """

    def authenticate(self, request):
        # Try header first
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)

        # Fallback: cookie
        raw_token = request.COOKIES.get(getattr(settings, "AUTH_COOKIE", "access_token"))
        if not raw_token:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        return (user, validated_token)
