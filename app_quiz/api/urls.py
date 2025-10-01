from django.urls import path
from app_quiz.api.views import CreateQuizFromYoutubeView

urlpatterns = [
    path("createQuiz/", CreateQuizFromYoutubeView.as_view(), name="create-quiz"),
]
