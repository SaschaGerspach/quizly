# tests/test_auth_register.py
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_register_returns_201_and_creates_user(api_client):
    """Happy path. Expect 201 and a persisted user."""
    url = reverse("auth-register")
    payload = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "StrongPass123",
        "confirmed_password": "StrongPass123",
    }
    res = api_client.post(url, payload, format="json")
    assert res.status_code == 201
    assert res.data == {"detail": "User created successfully!"}
    assert User.objects.filter(username="alice", email="alice@example.com").exists()


@pytest.mark.django_db
def test_register_rejects_password_mismatch(api_client):
    """Expect 400 if passwords do not match."""
    url = reverse("auth-register")
    payload = {
        "username": "bob",
        "email": "bob@example.com",
        "password": "StrongPass123",
        "confirmed_password": "WrongPass123",
    }
    res = api_client.post(url, payload, format="json")
    assert res.status_code == 400
    assert "confirmed_password" in res.data


@pytest.mark.django_db
def test_register_rejects_duplicate_email(api_client):
    """Expect 400 if email already exists."""
    User.objects.create_user(username="tom", email="dup@example.com", password="xXx123456")
    url = reverse("auth-register")
    payload = {
        "username": "tom2",
        "email": "dup@example.com",
        "password": "StrongPass123",
        "confirmed_password": "StrongPass123",
    }
    res = api_client.post(url, payload, format="json")
    assert res.status_code == 400
    assert "email" in res.data
