import pytest
from django.contrib.auth.models import User
from django.test import Client

from apps.auth.services import create_access_token


@pytest.fixture
def api_client() -> Client:
    user = User.objects.create_user(
        username="test@example.com",
        email="test@example.com",
        password="testpass123",
    )
    token = create_access_token(user)
    client = Client()
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    client.user = user  # type: ignore[attr-defined]
    return client


@pytest.fixture
def auth_headers() -> dict[str, str]:
    user = User.objects.create_user(
        username="test@example.com",
        email="test@example.com",
        password="testpass123",
    )
    token = create_access_token(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}
