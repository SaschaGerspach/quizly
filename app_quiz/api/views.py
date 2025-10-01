from typing import List, Dict

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from app_auth.authentication import CookieJWTAuthentication
from app_quiz.models import Quiz, Question
from app_quiz.api.serializers import (
    CreateQuizRequestSerializer,
    QuizWithQuestionsSerializer,
)
from app_quiz import utils


class CreateQuizFromYoutubeView(APIView):
    """
    POST /api/createQuiz/

    Authenticated only. Creates a new quiz from a YouTube URL and returns
    the created quiz with all questions as specified.
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        req_ser = CreateQuizRequestSerializer(data=request.data)
        if not req_ser.is_valid():
            return Response(req_ser.errors, status=status.HTTP_400_BAD_REQUEST)

        url = req_ser.validated_data["url"]

        try:
            generated = utils.generate_quiz_from_youtube(url)
            # expected keys: title, description, questions
            title = (generated.get("title") or "").strip()
            description = generated.get("description") or ""
            questions_data: List[Dict] = generated.get("questions") or []
        except NotImplementedError as e:
            # Explicit 500 per spec if internal logic not implemented
            return Response(
                {"detail": "Internal error: quiz generation not implemented."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception:
            # Do not leak internals; return 500 per spec
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not title:
            return Response(
                {"detail": "Invalid generated data: title missing."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Create quiz
        quiz = Quiz.objects.create(
            owner=request.user,
            title=title,
            description=description,
            video_url=url,
        )

        # Create questions
        question_objs = []
        for q in questions_data:
            q_title = (q.get("question_title") or "").strip()
            q_options = q.get("question_options") or []
            q_answer = (q.get("answer") or "").strip()

            # Basic server-side sanity checks to avoid empty records
            if not q_title or not isinstance(q_options, list) or not q_options or not q_answer:
                continue

            question_objs.append(
                Question(
                    quiz=quiz,
                    question_title=q_title,
                    question_options=q_options,
                    answer=q_answer,
                )
            )
        if question_objs:
            Question.objects.bulk_create(question_objs)

        resp_ser = QuizWithQuestionsSerializer(instance=quiz)
        return Response(resp_ser.data, status=status.HTTP_201_CREATED)
