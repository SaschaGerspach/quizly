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
def test_patch_requires_auth(api_client, user_a):
    quiz = Quiz.objects.create(owner=user_a, title="T", description="D")
    resp = api_client.patch(f"/api/quizzes/{quiz.id}/", {"title": "X"}, format="json")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_patch_own_quiz_success(api_client, user_a):
    quiz = Quiz.objects.create(owner=user_a, title="Old", description="Desc")
    Question.objects.create(quiz=quiz, question_title="Q1", question_options=["A","B"], answer="A")
    login(api_client, user_a)
    resp = api_client.patch(f"/api/quizzes/{quiz.id}/", {"title": "Partially Updated Title"}, format="json")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Partially Updated Title"
    assert data["description"] == "Desc"
    assert "questions" in data and len(data["questions"]) == 1


@pytest.mark.django_db
def test_patch_forbidden_on_foreign_quiz(api_client, user_a, user_b):
    quiz = Quiz.objects.create(owner=user_b, title="Old", description="Desc")
    login(api_client, user_a)
    resp = api_client.patch(f"/api/quizzes/{quiz.id}/", {"title": "Hack"}, format="json")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_patch_not_found(api_client, user_a):
    login(api_client, user_a)
    resp = api_client.patch("/api/quizzes/999/", {"title": "X"}, format="json")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_patch_invalid_payload_returns_400(api_client, user_a):
    quiz = Quiz.objects.create(owner=user_a, title="Old", description="Desc")
    login(api_client, user_a)
    resp = api_client.patch(f"/api/quizzes/{quiz.id}/", {"title": "   "}, format="json")
    assert resp.status_code == 400
