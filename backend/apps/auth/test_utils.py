from django.contrib.auth.models import User
from django.test import Client

from apps.auth.services import create_access_token

TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpass123"


def make_auth_client() -> Client:
    user = User.objects.create_user(
        username=TEST_EMAIL,
        email=TEST_EMAIL,
        password=TEST_PASSWORD,
    )
    token = create_access_token(user)
    client = Client()
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    client.user = user  # type: ignore[attr-defined]
    return client
