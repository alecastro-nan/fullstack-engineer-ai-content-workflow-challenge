import os
from collections.abc import Generator

import pytest
from django.test import Client, override_settings

from apps.auth.test_utils import make_auth_client

os.environ.setdefault("SKIP_RATE_LIMIT", "1")


@pytest.fixture(autouse=True)
def _jwt_signing_key() -> Generator[None, None, None]:
    with override_settings(JWT_SIGNING_KEY="test-jwt-key-not-for-production"):
        yield


@pytest.fixture
def auth_client() -> Client:
    return make_auth_client()


# Override pytest-django's built-in `client` fixture with an authenticated one
@pytest.fixture
def client(auth_client: Client) -> Client:
    return auth_client
