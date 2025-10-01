from typing import Dict, List


def generate_quiz_from_youtube(url: str) -> Dict:
    """
    Generate quiz data from a YouTube URL.

    Returns a dict with keys:
      - title: str
      - description: str
      - questions: List[{
            "question_title": str,
            "question_options": List[str],
            "answer": str
        }]

    NOTE: This is intentionally left as a pure function stub. Implement the
    actual extraction later. The view and tests rely on this function's contract.
    """
    # Placeholder to be implemented in a later step.
    # Raise a clear error so implementers notice if it's called unmocked in tests.
    raise NotImplementedError("YouTube quiz generation is not implemented yet.")
