from rest_framework.permissions import BasePermission
from app_quiz.models import Quiz


class IsQuizOwner(BasePermission):
    """
    Grants access only to the owner of the quiz.
    """

    def has_object_permission(self, request, view, obj: Quiz):
        return obj.owner_id == request.user.id
