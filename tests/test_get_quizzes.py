# tests/test_get_quizzes.py

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
    return User.objects.create_user(username="alice", email="alice@example.com", password="password123")


@pytest.fixture
def user_b(db):
    return User.objects.create_user(username="bob", email="bob@example.com", password="password123")


def login(client, user, password="password123"):
    resp = client.post("/api/login/", {"username": user.username, "password": password}, format="json")
    assert resp.status_code == 200
    return client


@pytest.mark.django_db
def test_requires_auth(api_client):
    resp = api_client.get("/api/quizzes/")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_returns_only_own_quizzes(api_client, user_a, user_b):
    quiz_a = Quiz.objects.create(owner=user_a, title="Quiz A", description="Desc A", video_url="https://youtu.be/aaa")
    Question.objects.create(
        quiz=quiz_a,
        question_title="Q1",
        question_options=["A", "B", "C"],
        answer="A",
    )
    Quiz.objects.create(owner=user_b, title="Quiz B", description="Desc B", video_url="https://youtu.be/bbb")

    login(api_client, user_a)
    resp = api_client.get("/api/quizzes/")
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    quiz = data[0]
    assert quiz["title"] == "Quiz A"
    assert quiz["video_url"] == "https://youtu.be/aaa"
    assert len(quiz["questions"]) == 1
    q = quiz["questions"][0]
    assert "id" in q
    assert "question_title" in q
    assert "question_options" in q
    assert "answer" in q
