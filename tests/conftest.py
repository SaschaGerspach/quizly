# tests/conftest.py
import sys
import types
import pytest
from rest_framework.test import APIClient

# ---- yt_dlp Stub (inkl. Untermodul yt_dlp.utils.DownloadError) ----
yt_dlp_mod = types.ModuleType("yt_dlp")

class _FakeYDL:
    def __init__(self, *args, **kwargs): pass
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): pass
    def download(self, *args, **kwargs): return 0  # pretend success

yt_dlp_mod.YoutubeDL = _FakeYDL
sys.modules["yt_dlp"] = yt_dlp_mod

yt_dlp_utils_mod = types.ModuleType("yt_dlp.utils")
class DownloadError(Exception):
    """Stubbed DownloadError to satisfy 'from yt_dlp.utils import DownloadError'."""
    pass

yt_dlp_utils_mod.DownloadError = DownloadError
sys.modules["yt_dlp.utils"] = yt_dlp_utils_mod

# ---- whisper Stub ----
whisper_mod = types.ModuleType("whisper")

class _FakeWhisperModel:
    def transcribe(self, *args, **kwargs):
        return {"text": "dummy transcript"}

def load_model(*args, **kwargs):
    return _FakeWhisperModel()

whisper_mod.load_model = load_model
sys.modules["whisper"] = whisper_mod

# ---- google.generativeai Stub ----
genai_mod = types.ModuleType("google.generativeai")

def configure(**kwargs):
    # no-op
    return None

class _FakeResp:
    # mimic .text attribute the code reads
    text = (
        '{"title":"Quiz Title","description":"Quiz Description",'
        '"questions":[{"question_title":"Question 1",'
        '"question_options":["Option A","Option B","Option C","Option D"],'
        '"answer":"Option A"}]}'
    )

class GenerativeModel:
    def __init__(self, name): self.name = name
    def generate_content(self, prompt): return _FakeResp()

genai_mod.configure = configure
genai_mod.GenerativeModel = GenerativeModel
sys.modules["google.generativeai"] = genai_mod

# Optional: stub google package container to avoid weird import chains
google_pkg = types.ModuleType("google")
google_pkg.generativeai = genai_mod
sys.modules["google"] = google_pkg

# ---- common test fixtures ----
@pytest.fixture
def api_client():
    return APIClient()
