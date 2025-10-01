from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer
from .permissions import IsAnonymousOnly, RequiresValidRefreshCookie
from ..utils import create_user_from_payload, set_auth_cookies, build_user_payload, set_access_cookie
from django.conf import settings


class RegisterView(APIView):
    """
    POST /api/register/
    Registers a new user account.
    Returns 201 on success with a short detail message.
    """
    permission_classes = [
        IsAnonymousOnly]  # matches "No permissions required" for auth'd users

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Delegate creation to utils; keep view free of business logic.
        create_user_from_payload(serializer.validated_data)

        return Response({"detail": "User created successfully!"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    POST /api/login/
    Authenticates a user and sets JWT auth cookies.
    Returns 200 on success with a short detail message.
    """
    permission_classes = [
        IsAnonymousOnly]  # matches "No permissions required" for auth'd users

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        # Token generation and cookie setting logic would go here.
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        payload = {
            "detail": "Login successfully!",
            "user": build_user_payload(user),
        }

        response = Response(payload, status=status.HTTP_200_OK)
        set_auth_cookies(response, str(access), str(refresh))

        return response


class LogoutView(APIView):
    """Log out user and blacklist refresh token."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        refresh_token = request.COOKIES.get(
            getattr(settings, "REFRESH_COOKIE", "refresh_token")
        )
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        response = Response(
            {
                "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
            },
            status=status.HTTP_200_OK,
        )

        # Remove cookies
        response.delete_cookie(
            key=getattr(settings, "AUTH_COOKIE", "access_token"),
            path=getattr(settings, "AUTH_COOKIE_PATH", "/"),
        )
        response.delete_cookie(
            key=getattr(settings, "REFRESH_COOKIE", "refresh_token"),
            path=getattr(settings, "REFRESH_COOKIE_PATH", "/"),
        )

        return response
    

class TokenRefreshView(APIView):
    """
    POST /api/token/refresh/
    Spec: reads refresh token from cookie, returns new access token
    and sets it as cookie. No request body required.
    """
    permission_classes = [RequiresValidRefreshCookie]

    def post(self, request):
        cookie_name = getattr(settings, "REFRESH_COOKIE", "refresh_token")
        raw_refresh = request.COOKIES.get(cookie_name)

        # We already validated in the permission, but re-parse to mint a new access
        refresh = RefreshToken(raw_refresh)
        new_access = refresh.access_token

        payload = {
            "detail": "Token refreshed",
            "access": str(new_access),
        }
        response = Response(payload, status=status.HTTP_200_OK)
        set_access_cookie(response, str(new_access))
        return response
