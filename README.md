# Quizly (Backend)

**Quizly Backend** is a Django REST API that automatically generates interactive quizzes from YouTube videos.  
It downloads a video, extracts its audio, transcribes the speech using **Whisper AI**, and generates multiple-choice questions with **Google Gemini**.

---

## 🚀 Features

- Fully functional **Django REST API**
- **JWT cookie authentication** (login, logout, token refresh)
- **Automatic quiz generation** from YouTube videos  
  (supported formats: `youtube.com/watch?v=...`, `youtu.be/...`, `youtube.com/live/...`)
- **Integration with external tools:**
  - `yt-dlp` for downloading YouTube videos
  - `ffmpeg` for extracting audio
  - `openai-whisper` for speech-to-text transcription
  - `google-generativeai` (Gemini) for question generation
- Comprehensive **pytest** test suite (87% coverage)
- Excludes **YouTube Shorts** by design

---

##  Quickstart (Development)

### 1. Virtual environment
```bash
python -m venv .venv
```

### 2. Activate env
#### 2.1 Windows
```bash
.venv\Scripts\activate
```
#### 2.2 Mac/Linux
```bash
.venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt

```

### 4. Create a .env File

```bash
python manage.py migrate
```

In the project root, create a .env file containing:

```bash
SECRET_KEY=<your_django_secret>
DEBUG=True
GEMINI_API_KEY=<your_gemini_api_key>
```

### 5. Start development server
```bash
python manage.py runserver
```

## Run Tests

```bash
pytest
```

With coverage report:
```bash
pytest --cov
```