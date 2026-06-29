import os

import pytest
from django.test import Client

from apps.auth.test_utils import make_auth_client

os.environ.setdefault("SKIP_RATE_LIMIT", "1")


@pytest.fixture
def auth_client() -> Client:
    return make_auth_client()


# Override pytest-django's built-in `client` fixture with an authenticated one
@pytest.fixture
def client(auth_client: Client) -> Client:
    return auth_client
