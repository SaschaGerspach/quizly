import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestLogin:
    def setup_method(self):
        """Setup a user for login tests."""
        self.client = APIClient()
        self.password = "testpassword123"
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=self.password,
        )

    def test_login_successful(self):
        """Login should succeed with correct credentials."""
        response = self.client.post(
            "/api/login/",
            {"username": self.user.username, "password": self.password},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["detail"] == "Login successfully!"
        assert data["user"]["username"] == self.user.username
        assert data["user"]["email"] == self.user.email
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    def test_login_invalid_password(self):
        """Login should fail with wrong password."""
        response = self.client.post(
            "/api/login/",
            {"username": self.user.username, "password": "wrongpass"},
            format="json",
        )
        assert response.status_code == 401

    def test_login_invalid_user(self):
        """Login should fail with unknown username."""
        response = self.client.post(
            "/api/login/",
            {"username": "not_existing", "password": "whatever"},
            format="json",
        )
        assert response.status_code == 401
