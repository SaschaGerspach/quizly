from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from .permissions import IsAnonymousOnly
from ..utils import create_user_from_payload


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
