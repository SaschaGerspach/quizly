import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from app_quiz import utils

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_a(db):
    return User.objects.create_user(username="alice", email="alice@example.com", password="password123")


def login(client, user, password: str):
    resp = client.post("/api/login/", {"username": user.username, "password": password}, format="json")
    assert resp.status_code == 200, getattr(resp, "data", resp.content)
    return client


@pytest.mark.django_db
def test_requires_auth(api_client):
    resp = api_client.post("/api/createQuiz/", {"url": "https://www.youtube.com/watch?v=abc"}, format="json")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_rejects_non_youtube_url(api_client, user_a):
    login(api_client, user_a, "password123")
    resp = api_client.post("/api/createQuiz/", {"url": "https://vimeo.com/123"}, format="json")
    assert resp.status_code == 400
    assert "url" in resp.json()


@pytest.mark.django_db
def test_success_creates_quiz_and_questions(api_client, user_a, monkeypatch):
    login(api_client, user_a, "password123")

    def fake_generate(url: str):
        assert url == "https://www.youtube.com/watch?v=example"
        return {
            "title": "Quiz Title",
            "description": "Quiz Description",
            "questions": [
                {
                    "question_title": "Question 1",
                    "question_options": ["Option A", "Option B", "Option C", "Option D"],
                    "answer": "Option A",
                }
            ],
        }

    # Monkeypatch the utils function so we don't depend on external services
  
    monkeypatch.setattr(utils, "generate_quiz_from_youtube", fake_generate)

    payload = {"url": "https://www.youtube.com/watch?v=example"}
    resp = api_client.post("/api/createQuiz/", payload, format="json")
    assert resp.status_code == 201

    data = resp.json()
    assert data["title"] == "Quiz Title"
    assert data["description"] == "Quiz Description"
    assert data["video_url"] == "https://www.youtube.com/watch?v=example"
    assert isinstance(data["questions"], list)
    assert len(data["questions"]) == 1
    q = data["questions"][0]
    assert q["question_title"] == "Question 1"
    assert q["question_options"] == ["Option A", "Option B", "Option C", "Option D"]
    assert q["answer"] == "Option A"
    assert "created_at" in q and "updated_at" in q


@pytest.mark.django_db
def test_internal_error_propagates_as_500(api_client, user_a, monkeypatch):
    login(api_client, user_a, "password123")

    def fake_generate(url: str):
        raise RuntimeError("boom")

  
    monkeypatch.setattr(utils, "generate_quiz_from_youtube", fake_generate)

    resp = api_client.post("/api/createQuiz/", {"url": "https://www.youtube.com/watch?v=xyz"}, format="json")
    assert resp.status_code == 500
