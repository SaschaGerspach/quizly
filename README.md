# Quizly Backend

Quizly is a Django REST API that transforms YouTube videos into interactive, multiple-choice quizzes. The pipeline downloads source videos with `yt-dlp`, extracts audio via `ffmpeg`, transcribes speech using Whisper, and asks Google Gemini to generate the questions.

---

## Table of Contents
- [Overview](#overview)
- [Feature Highlights](#feature-highlights)
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Environment Variables](#environment-variables)
- [Example Usage](#example-usage)
- [API Overview](#api-overview)
- [Tests](#tests)
- [Docker](#docker)
- [Production Notes](#production-notes)
- [License](#license)

---

## Overview

Quizly powers a frontend that lets authenticated users create, review, and manage quizzes derived from YouTube content. Authentication relies on JWTs stored in HttpOnly cookies so browsers can remain stateless while staying secure. Quiz logic resides in `app_quiz`, while authentication and permissions live in `app_auth`.

---

## Feature Highlights
- Django 5 and Django REST Framework foundation with clear app boundaries
- Cookie-based JWT authentication covering login, logout, refresh, and registration
- Automatic quiz generation from YouTube URLs (Shorts intentionally excluded)
- Integrations for `yt-dlp`, `ffmpeg`, Whisper, and Google Gemini
- Pytest suite with high coverage and fixtures simulating realistic flows
- Dockerfile shipping Gunicorn-ready production image
- Configurable token lifetimes, cookie policies, and media storage paths

---

## Prerequisites
- Python 3.12
- `pip` (or `pipx`)
- System-wide `ffmpeg` available on `PATH`
- Google Gemini API key
- Optional: Docker or Docker Compose for container workflows
- Sufficient disk to store temporary downloads and transcripts

---

## Local Development

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd quizly
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate the environment**
   - Windows PowerShell:
     ```bash
     .venv\Scripts\Activate.ps1
     ```
   - macOS / Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Create `.env`**
   Copy or adapt the template from [Environment Variables](#environment-variables).

6. **Run database migrations**
   ```bash
   python manage.py migrate
   ```
   Optional superuser:
   ```bash
   python manage.py createsuperuser
   ```
   Use those credentials to reach the Django admin at `http://127.0.0.1:8000/admin/`.

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```
   The API listens on `http://127.0.0.1:8000/` by default.

---

## Environment Variables

Suggested `.env` for local work:

```bash
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:5500,http://localhost:5500

GEMINI_API_KEY=<your_gemini_api_key>
GEMINI_MODEL=gemini-2.0-flash
FFMPEG_PATH=ffmpeg
WHISPER_MODEL=base
```

Additional knobs exposed in `core/settings.py`:

| Variable | Required | Description |
| -------- | -------- | ----------- |
| `DJANGO_SECRET_KEY` | yes | Keep secret in production. |
| `DJANGO_DEBUG` | recommended | `True` locally, `False` in production. |
| `DJANGO_ALLOWED_HOSTS` | yes | Comma-separated list of valid hosts. |
| `CORS_ALLOWED_ORIGINS` | frontend only | Origins allowed to receive cookies. |
| `CSRF_TRUSTED_ORIGINS` | frontend only | Origins allowed to send CSRF requests. |
| `GEMINI_API_KEY` | yes | Token for Google Gemini question generation. |
| `GEMINI_MODEL` | optional | Alternate model, e.g., `gemini-1.5-pro`. |
| `FFMPEG_PATH` | optional | Explicit path when `ffmpeg` is not on `PATH`. |
| `WHISPER_MODEL` | optional | Whisper model size (`tiny`, `base`, `small`, …). |
| `JWT_ACCESS_LIFETIME_MIN` | optional | Access token lifetime in minutes. |
| `JWT_REFRESH_LIFETIME_DAYS` | optional | Refresh token lifetime in days. |
| `JWT_ACCESS_COOKIE_NAME` | optional | Cookie name for the access token. |
| `JWT_REFRESH_COOKIE_NAME` | optional | Cookie name for the refresh token. |
| `JWT_COOKIE_SAMESITE` | optional | Cookie policy (`Lax`, `Strict`, `None`). |
| `MEDIA_ROOT` | optional | File system path for stored media. |

---

## Example Usage

After starting the server:

1. Register or log in at `/api/login/`.
2. Send a YouTube link to `/api/createQuiz/`.
3. Receive a generated quiz with multiple-choice questions.

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/createQuiz/ \
  -H "Content-Type: application/json" \
  --cookie "access_token=<your_access_token>" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

Example response:

```json
{
  "id": 3,
  "title": "Machine Learning Basics",
  "questions": [
    {
      "question": "What is supervised learning?",
      "choices": ["Using labeled data", "Using unlabeled data"],
      "correct": 0
    }
  ]
}
```

---

## API Overview

All routes are served under `/api/` and expect valid cookies unless noted.

**Authentication (`app_auth`)**
- `POST /api/register/` — Register a new user (only accessible for unauthenticated users).
- `POST /api/login/` — Obtain access and refresh cookies.
- `POST /api/logout/` — Clear cookies and blacklist refresh token.
- `POST /api/token/refresh/` — Issue a fresh access token from the refresh cookie.

**Quiz Management (`app_quiz`)**
- `POST /api/createQuiz/` — Generate a quiz from a YouTube URL.
- `GET /api/quizzes/` — List quizzes owned by the authenticated user.
- `GET /api/quizzes/<id>/` — Retrieve a quiz with questions.
- `PATCH /api/quizzes/<id>/` — Update quiz title or description.
- `DELETE /api/quizzes/<id>/` — Delete a quiz and its questions.

---

## Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov
```

Fixtures under `tests/` ensure that tests remain fast and deterministic.

---

## Docker

The provided Dockerfile builds a production-ready image running Gunicorn.

Build:
```bash
docker build -t quizly-backend .
```

Run:
```bash
docker run --env-file .env -p 8001:8001 quizly-backend
```

On startup the container applies migrations automatically and exposes port 8001.
The service listens on port 8001 inside the container and can be mapped as needed (e.g., -p 8000:8001 for local use).

---

## Production Notes
- Terminate SSL before Django so cookie flags such as `Secure` are honored.
- Ship long-lived assets (downloads, transcripts) to external storage.
- Introduce background workers if processing time grows with load.
- Monitor `MEDIA_ROOT` usage when handling many downloads.

---

## License

License information is pending. Treat the project as proprietary until a license is published.

