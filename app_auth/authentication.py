from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
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

class EmailOrUsernameBackend(ModelBackend):
    """
    Allows login with either username or email address.
    Automatically used by Django when added in settings.py.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()

        # Falls das Frontend "email" statt "username" sendet
        if username is None:
            username = kwargs.get("email")

        if not username or not password:
            return None

        try:
            # Wenn ein @ enthalten ist, wird nach E-Mail gesucht
            if "@" in username:
                user = User.objects.get(email__iexact=username)
            else:
                user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return None

        return user if user.check_password(password) else None