from typing import Any
from urllib.parse import urlparse

from rest_framework import serializers
from app_quiz.models import Quiz, Question


class CreateQuizRequestSerializer(serializers.Serializer):
    url = serializers.URLField()

    def validate_url(self, value: str) -> str:
        """
        Accept only YouTube URLs as per spec. No extras.
        """
        parsed = urlparse(value)
        host = (parsed.netloc or "").lower()
        if not (
            host.endswith("youtube.com")
            or host == "youtu.be"
            or host.endswith(".youtube.com")
        ):
            raise serializers.ValidationError("Only YouTube URLs are allowed.")
        return value


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class QuizWithQuestionsSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "video_url", "questions"]
