from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer
from .permissions import IsAnonymousOnly
from ..utils import create_user_from_payload, set_auth_cookies, build_user_payload


class RegisterView(APIView):
    """
    POST /api/register/
    Registers a new user account.
    Returns 201 on success with a short detail message.
    """
    permission_classes = [IsAnonymousOnly]  # matches "No permissions required" for auth'd users

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
    permission_classes = [IsAnonymousOnly]  # matches "No permissions required" for auth'd users

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
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