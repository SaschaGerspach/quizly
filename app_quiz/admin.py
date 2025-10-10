# app_quiz/admin.py
from django.contrib import admin
from .models import Quiz, Question


class QuestionInline(admin.TabularInline):
    """Inline editor for questions inside a quiz."""
    model = Question
    extra = 0
    fields = ("question_title", "question_options", "answer", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin for quizzes with inline questions and useful filters."""
    list_display = ("id", "title", "owner", "video_url", "questions_count", "created_at", "updated_at")
    list_select_related = ("owner",)
    list_filter = ("created_at", "updated_at", "owner")
    search_fields = ("title", "description", "video_url", "owner__username", "owner__email")
    readonly_fields = ("created_at", "updated_at")
    inlines = [QuestionInline]
    ordering = ("-created_at",)

    @admin.display(description="Questions")
    def questions_count(self, obj: Quiz) -> int:
        # Cheap aggregate; if performance becomes an issue, annotate in queryset.
        return obj.questions.count()

    def get_queryset(self, request):
        """Annotate/optimize the queryset and restrict to own objects for non-superusers."""
        qs = super().get_queryset(request).select_related("owner").prefetch_related("questions")
        if request.user.is_superuser:
            return qs
        # Non-superusers see only their own quizzes
        return qs.filter(owner=request.user)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Separate admin for questions when not editing via inline."""
    list_display = ("id", "quiz", "question_title", "answer", "created_at", "updated_at")
    list_select_related = ("quiz", "quiz__owner")
    search_fields = ("question_title", "answer", "quiz__title", "quiz__owner__username")
    list_filter = ("created_at", "updated_at", "quiz__owner")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
