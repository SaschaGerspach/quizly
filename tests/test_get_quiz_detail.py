# tests/test_get_quiz_detail.py
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from app_quiz.models import Quiz, Question

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_a(db):
    return User.objects.create_user(username="alice", password="password123")


@pytest.fixture
def user_b(db):
    return User.objects.create_user(username="bob", password="password123")


def login(client, user, password="password123"):
    resp = client.post("/api/login/", {"username": user.username, "password": password}, format="json")
    assert resp.status_code == 200
    return client


@pytest.mark.django_db
def test_requires_auth(api_client, user_a):
    quiz = Quiz.objects.create(owner=user_a, title="Quiz A", description="Desc", video_url="https://youtu.be/a")
    resp = api_client.get(f"/api/quizzes/{quiz.id}/")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_retrieve_own_quiz(api_client, user_a):
    quiz = Quiz.objects.create(owner=user_a, title="Quiz A", description="Desc", video_url="https://youtu.be/a")
    Question.objects.create(
        quiz=quiz,
        question_title="Q1",
        question_options=["A", "B", "C"],
        answer="A",
    )
    login(api_client, user_a)
    resp = api_client.get(f"/api/quizzes/{quiz.id}/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Quiz A"
    assert data["video_url"] == "https://youtu.be/a"
    assert len(data["questions"]) == 1
    assert data["questions"][0]["answer"] == "A"


@pytest.mark.django_db
def test_forbidden_on_foreign_quiz(api_client, user_a, user_b):
    quiz = Quiz.objects.create(owner=user_b, title="Quiz B", description="Desc", video_url="https://youtu.be/b")
    login(api_client, user_a)
    resp = api_client.get(f"/api/quizzes/{quiz.id}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_not_found(api_client, user_a):
    login(api_client, user_a)
    resp = api_client.get("/api/quizzes/999/")
    assert resp.status_code == 404
