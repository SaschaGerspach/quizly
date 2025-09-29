import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    """DRF API client for request testing."""
    return APIClient()
