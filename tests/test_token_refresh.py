import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.django_db
class TestTokenRefresh:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="refresh_user",
            email="r@example.com",
            password="testpassword123",
        )
        self.refresh = RefreshToken.for_user(self.user)

    def test_refresh_success(self):
        """Should return 200 with new access token and set access cookie."""
        self.client.cookies["refresh_token"] = str(self.refresh)
        resp = self.client.post("/api/token/refresh/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["detail"] == "Token refreshed"
        assert isinstance(data["access"], str) and len(data["access"]) > 10
        # cookie set
        assert "access_token" in resp.cookies

    def test_refresh_missing_cookie(self):
        """Should return 401 when refresh cookie is missing."""
        resp = self.client.post("/api/token/refresh/")
        assert resp.status_code == 401
