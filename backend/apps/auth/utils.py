from django.conf import settings
from django.contrib.auth.models import User
from graphql import GraphQLError
from strawberry.types.info import Info


def extract_bearer_token(request: object) -> str | None:
    headers = getattr(request, "headers", {})
    raw = headers.get("Authorization", b"")
    if isinstance(raw, bytes):
        raw = raw.decode()
    if isinstance(raw, str) and raw.startswith("Bearer "):
        return raw[len("Bearer "):]
    return None


def get_user_or_error(info: Info) -> User | None:
    user: User | None = getattr(info.context, "user", None)
    if user is None and getattr(settings, "AUTH_REQUIRED", True):
        raise GraphQLError("Authentication required")
    return user
