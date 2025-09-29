from typing import Dict
from django.contrib.auth import get_user_model

User = get_user_model()


def create_user_from_payload(data: Dict) -> User:
    """
    Create a new user using Django's user manager.
    Only simple orchestration lives here to keep views thin and testable.
    """
    user = User.objects.create_user(
        username=data["username"],
        email=data["email"],
        password=data["password"],
    )
    return user
