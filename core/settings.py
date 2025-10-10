# core/settings.py
import os
from dotenv import load_dotenv
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "corsheaders",
    # Optional: Blacklist, falls wir Refresh Tokens invalidieren wollen
    "rest_framework_simplejwt.token_blacklist",
    # Local apps
    "app_auth",
    "app_quiz",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

# Datenbank vorerst SQLite (später gern Postgres)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Static/Media (einfacher Start)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv("MEDIA_ROOT", str(BASE_DIR / "media"))

# CORS/CSRF für Cookie-Auth
CORS_ALLOWED_ORIGINS = [o for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o]
CORS_ALLOW_CREDENTIALS = True  # wichtig für Cookies

CSRF_TRUSTED_ORIGINS = [o for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o]
CSRF_COOKIE_SECURE = not DEBUG                       # nur über HTTPS senden
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "Lax")
SESSION_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "Lax")

# JWT in HttpOnly-Cookies (Namen/Policy, die Views nutzen)
AUTH_COOKIE = os.getenv("JWT_ACCESS_COOKIE_NAME", "access_token")
REFRESH_COOKIE = os.getenv("JWT_REFRESH_COOKIE_NAME", "refresh_token")
AUTH_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "Lax")  # "Lax" oder "Strict"
AUTH_COOKIE_SECURE = not DEBUG
AUTH_COOKIE_PATH = "/"
REFRESH_COOKIE_PATH = "/"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "app_auth.authentication.CookieJWTAuthentication",
        # Wir ergänzen später noch eine kleine Klasse, die das JWT aus dem Cookie liest.
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# SimpleJWT – Laufzeiten aus Env
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("JWT_ACCESS_LIFETIME_MIN", "15"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.getenv("JWT_REFRESH_LIFETIME_DAYS", "30"))
    ),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),  # bleibt, auch wenn wir Cookies setzen
    "UPDATE_LAST_LOGIN": True,
}

# Logging (kurz und hilfreich für Dev)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

# Quiz-Pipeline Env (nur als Platzhalter, wir nutzen sie später)
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")  # global installiert → Name reicht
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY", "")


# Templates (required for admin)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # optional: eigener Templates-Ordner
        "APP_DIRS": True,                  # lädt templates/ in Apps automatisch
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]