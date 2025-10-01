import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.django_db
class TestLogout:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword123", email="test@example.com"
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)

        # Set cookies for authentication
        self.client.cookies["access_token"] = self.access_token
        self.client.cookies["refresh_token"] = self.refresh_token

    def test_logout_success(self):
        response = self.client.post("/api/logout/")
        assert response.status_code == 200
        assert "Log-Out successfully!" in response.data["detail"]

    def test_logout_unauthenticated(self):
        client = APIClient()  # no cookies set
        response = client.post("/api/logout/")
        assert response.status_code == 401
