# app_quiz/utils.py
from __future__ import annotations

import json
import os
import random
import re
import tempfile
from typing import Dict, List, Tuple
from urllib.parse import parse_qs, urlparse
from yt_dlp.utils import DownloadError

import google.generativeai as genai
import whisper
import yt_dlp


# --------------------------- helpers ---------------------------

_YT_HOSTS = ("youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be")


def _parse_video_id(url: str) -> Tuple[str, str]:
    """
    Parse a YouTube URL (watch?v=, youtu.be/<id>, /live/<id>)
    and return (video_id, normalized_watch_url). Returns ("","") if invalid.
    Shorts URLs are explicitly rejected.
    """
    p = urlparse(url)
    host = (p.netloc or "").lower()
    host = host.replace("www.", "")
    if host not in {"youtube.com", "m.youtube.com", "youtu.be"}:
        return "", ""

    path = p.path or ""

    if host == "youtu.be":
        vid = path.strip("/").split("/")[0]
    else:
        if path.lower().startswith("/shorts/"):
            raise ValueError("YouTube Shorts are not supported.")
        # support /shorts/<id> and /live/<id>
        m = re.match(r"^/live/([A-Za-z0-9_-]{5,})", path)
        if m:
            vid = m.group(1)
        else:
            qs = parse_qs(p.query)
            vid = (qs.get("v") or [""])[0]

    if not vid:
        raise ValueError("Invalid YouTube URL.")

    return vid, f"https://www.youtube.com/watch?v={vid}"

def _download_audio_to(tempdir: str, video_url: str) -> str:
    """
    Download audio using yt_dlp into tempdir as .m4a (requires ffmpeg).
    Returns absolute path to the produced .m4a file.
    Hardened against HTTP 403 by setting headers and options.
    """
    outtmpl = os.path.join(tempdir, "audio.%(ext)s")

    # Allow overriding UA/cookies via env for local quirks
    ua = os.getenv("YTDLP_UA", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/124.0.0.0 Safari/537.36")
    cookies_browser = os.getenv("YTDLP_COOKIES_FROM_BROWSER", "").strip().lower()  # e.g. "chrome", "edge", "firefox"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "quiet": True,
        "noprogress": True,
        "noplaylist": True,
        "concurrent_fragment_downloads": 1,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "http_headers": {
            "User-Agent": ua,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.8",
            "Referer": "https://www.youtube.com/",
        },
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
                "preferredquality": "192",
            }
        ],
        # You can uncomment this if your network has IPv6 issues:
        # "force_ip": "v4",
    }

    if cookies_browser in {"chrome", "edge", "firefox"}:
        # Optional: use local browser cookies (helps with age/region/captcha walls)
        ydl_opts["cookiesfrombrowser"] = (cookies_browser,)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except DownloadError as e:
        # Make the error explicit in logs; the view still returns 500 as per spec
        raise RuntimeError(f"yt-dlp failed to fetch audio (possible 403): {e}") from e

    for fname in os.listdir(tempdir):
        if fname.lower().endswith(".m4a"):
            return os.path.join(tempdir, fname)
    raise RuntimeError("Audio download succeeded but no .m4a file was produced.")



def _transcribe(audio_path: str) -> str:
    """
    Transcribe audio to text using Whisper.
    """
    model = whisper.load_model("small")  # "base" schneller, "small" bessere Qualität
    result = model.transcribe(audio_path, temperature=0, fp16=False)
    text = (result.get("text") or "").strip()
    if not text:
        raise RuntimeError("Transcription produced empty text.")
    return text


def _build_prompt(transcript: str, title_hint: str) -> str:
    """
    Prompt for Gemini to produce MC questions as strict JSON.
    """
    return f"""
You are a quiz generator. Create multiple-choice questions from the given transcript.
Rules:
- Return STRICT JSON only, no prose, no code fences.
- JSON schema:
{{
  "title": string,
  "description": string,
  "questions": [
    {{
      "question_title": string,
      "question_options": [string, string, string, string],
      "answer": string
    }}
  ]
}}
- Produce 10 questions.
- Options must be concise; one correct answer, three plausible distractors.
- Keep the language of the transcript.

title_hint: "{title_hint}"

transcript:
\"\"\"{transcript[:12000]}\"\"\"  // truncated for safety
"""


def _call_gemini(prompt: str, api_key: str) -> str:
    """
    Call Gemini and return the (possibly fenced) text.
    """
    model_name = os.getenv("GEMINI_MODEL")
    if not model_name:
        # 2) Auto-Detect: nimm ein verfügbares Modell mit generateContent
        try:
            avail = [
                (m.name.split("/")[-1], getattr(m, "supported_generation_methods", []))
                for m in genai.list_models()
            ]
            supported = [name for (name, methods) in avail if "generateContent" in methods]
            # Bevorzugte Reihenfolge:
            preferred = [
                "gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest",
                "gemini-pro-latest", "gemini-2.5-pro", "gemini-2.0-pro"
            ]
            for cand in preferred:
                if cand in supported:
                    model_name = cand
                    break
            if not model_name and supported:
                model_name = supported[0]  # irgendein unterstütztes Modell
        except Exception:
            # Fallback, falls list_models nicht klappt
            model_name = "gemini-flash-latest"

    model = genai.GenerativeModel(model_name)
    resp = model.generate_content(prompt)

    txt = (getattr(resp, "text", None) or "").strip()
    txt = re.sub(r"^```json\s*|\s*```$", "", txt, flags=re.IGNORECASE | re.MULTILINE)
    return txt

def _validate_and_fix(payload: Dict) -> Dict:
    """
    Ensure required keys and sane values. Fix minor issues deterministically.
    """
    title = (payload.get("title") or "Quiz Title").strip()
    description = (payload.get("description") or "Quiz Description").strip()
    questions_in = payload.get("questions") or []
    out_questions: List[Dict] = []

    rng = random.Random(42)

    for q in questions_in:
        qt = (q.get("question_title") or "").strip()
        opts = q.get("question_options") or []
        ans = (q.get("answer") or "").strip()

        opts = [str(o).strip() for o in opts if str(o).strip()]

        # Ensure exactly 4 options
        if len(opts) < 4:
            while len(opts) < 4:
                opts.append(f"Option {chr(ord('A') + len(opts))}")
        elif len(opts) > 4:
            if ans in opts:
                keep = [ans] + [o for o in opts if o != ans]
                opts = keep[:4]
            else:
                opts = opts[:4]

        # Ensure answer is in options
        if ans not in opts:
            ans = opts[0]

        if qt:
            out_questions.append(
                {
                    "question_title": qt,
                    "question_options": opts,
                    "answer": ans,
                }
            )

    if not out_questions:
        out_questions = [
            {
                "question_title": "What is the main topic of the video?",
                "question_options": ["Topic A", "Topic B", "Topic C", "Topic D"],
                "answer": "Topic A",
            }
        ]

    return {"title": title, "description": description, "questions": out_questions}


# ------------------------ public entry point ------------------------

def generate_quiz_from_youtube(url: str) -> Dict:
    """
    Full implementation:
    - validate/parse YouTube URL
    - download audio with yt_dlp (ffmpeg required)
    - transcribe with Whisper
    - generate MC-questions via Gemini (JSON)
    - validate/normalize output

    Returns dict with keys: title, description, questions[].
    Raises ValueError/RuntimeError on failures.
    """
    video_id, norm_url = _parse_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL.")

    # 1) Download + Transcribe
    with tempfile.TemporaryDirectory() as td:
        audio_path = _download_audio_to(td, norm_url)
        transcript = _transcribe(audio_path)

    # 2) Ask Gemini to produce quiz JSON
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not configured.")

    title_hint = f"YouTube Video {video_id}"
    prompt = _build_prompt(transcript, title_hint)
    raw = _call_gemini(prompt, api_key)

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raw_strip = raw.strip()
        if raw_strip.startswith("{") and raw_strip.endswith("}"):
            parsed = json.loads(raw_strip)
        else:
            raise RuntimeError("Gemini did not return valid JSON.")

    return _validate_and_fix(parsed)
