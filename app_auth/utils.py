from typing import Dict
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def create_user_from_payload(data: Dict) -> User:
    """
    Create a new user using Django's user manager.
    Only simple orchestration lives here to keep views thin and testable.
    """
    user = User.objects.create_user(
        username=data["username"],
        email=data["email"],
        password=data["password"],
    )
    return user

def _lifetime_seconds(key: str) -> int:
    lifetime = settings.SIMPLE_JWT.get(key, timedelta(minutes=5))
    return int(lifetime.total_seconds()) if isinstance(lifetime, timedelta) else int(lifetime)


def set_auth_cookies(response, access_token: str, refresh_token: str) -> None:
    """Set HttpOnly JWT cookies per settings (names/options from settings)."""
    response.set_cookie(
        key=getattr(settings, "AUTH_COOKIE", "access_token"),
        value=access_token,
        max_age=_lifetime_seconds("ACCESS_TOKEN_LIFETIME"),
        httponly=True,
        secure=getattr(settings, "AUTH_COOKIE_SECURE", True),
        samesite=getattr(settings, "AUTH_COOKIE_SAMESITE", "Lax"),
        path=getattr(settings, "AUTH_COOKIE_PATH", "/"),
    )
    response.set_cookie(
        key=getattr(settings, "REFRESH_COOKIE", "refresh_token"),
        value=refresh_token,
        max_age=_lifetime_seconds("REFRESH_TOKEN_LIFETIME"),
        httponly=True,
        secure=getattr(settings, "AUTH_COOKIE_SECURE", True),
        samesite=getattr(settings, "AUTH_COOKIE_SAMESITE", "Lax"),
        path=getattr(settings, "REFRESH_COOKIE_PATH", "/"),
    )

def build_user_payload(user: User) -> Dict[str, str]:
    """Build a simple user payload for registration response."""
    return {
        "id": user.id,
        "username": user.username,
        "email": getattr(user, "email", "") or "",
    }
