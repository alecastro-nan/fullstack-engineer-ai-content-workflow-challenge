from datetime import UTC, datetime, timedelta
from typing import cast

import jwt
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from apps.auth.exceptions import InvalidCredentials, InvalidToken
from apps.auth.models import UserProfile

ACCESS_TOKEN_EXPIRY_MINUTES = 15
REFRESH_TOKEN_EXPIRY_DAYS = 7


def _get_jwt_secret() -> str:
    return cast(str, getattr(settings, "JWT_SIGNING_KEY", None) or settings.SECRET_KEY)


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _get_or_create_profile(user: User) -> UserProfile:
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def _build_token_payload(user: User, token_type: str, expiry: timedelta) -> dict[str, object]:
    profile = _get_or_create_profile(user)
    return {
        "user_id": user.pk,
        "type": token_type,
        "exp": _now() + expiry,
        "iat": _now(),
        "token_version": profile.token_version,
    }


def create_access_token(user: User) -> str:
    payload = _build_token_payload(user, "access", timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES))
    return jwt.encode(payload, _get_jwt_secret(), algorithm="HS256")


def create_refresh_token(user: User) -> str:
    payload = _build_token_payload(user, "refresh", timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS))
    return jwt.encode(payload, _get_jwt_secret(), algorithm="HS256")


def create_tokens(user: User) -> dict[str, str]:
    return {
        "access_token": create_access_token(user),
        "refresh_token": create_refresh_token(user),
    }


def decode_token(token: str) -> User:
    try:
        payload = jwt.decode(token, _get_jwt_secret(), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise InvalidToken("Token has expired") from None
    except jwt.InvalidTokenError:
        raise InvalidToken("Invalid token") from None

    if payload.get("type") not in ("access", "refresh"):
        raise InvalidToken("Invalid token type")

    user_id = payload.get("user_id")
    if user_id is None:
        raise InvalidToken("Invalid token payload")

    try:
        user = User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        raise InvalidToken("User not found") from None

    profile = _get_or_create_profile(user)
    token_version = payload.get("token_version", 0)
    if token_version != profile.token_version:
        raise InvalidToken("Token has been invalidated")

    return user


async def decode_token_async(token: str) -> User | None:
    try:
        return await sync_to_async(decode_token)(token)
    except InvalidToken:
        return None


def refresh_tokens(refresh_token: str) -> dict[str, str]:
    try:
        payload = jwt.decode(refresh_token, _get_jwt_secret(), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise InvalidToken("Refresh token has expired") from None
    except jwt.InvalidTokenError:
        raise InvalidToken("Invalid refresh token") from None
    if payload.get("type") != "refresh":
        raise InvalidToken("Invalid refresh token")
    user_id = payload.get("user_id")
    if user_id is None:
        raise InvalidToken("Invalid refresh token payload")
    try:
        user = User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        raise InvalidToken("User not found") from None

    profile = _get_or_create_profile(user)
    token_version = payload.get("token_version", 0)
    if token_version != profile.token_version:
        raise InvalidToken("Refresh token has been invalidated")

    return create_tokens(user)


def invalidate_user_tokens(user: User) -> None:
    profile = _get_or_create_profile(user)
    profile.token_version += 1
    profile.save(update_fields=["token_version"])


def register_user(email: str, password: str) -> User:
    if User.objects.filter(email=email).exists():
        raise InvalidCredentials("Registration failed")
    if len(password) < 8:
        raise InvalidCredentials("Password must be at least 8 characters")
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
    )
    return user


def login_user(email: str, password: str) -> User:
    user = authenticate(username=email, password=password)
    if user is None:
        raise InvalidCredentials("Invalid email or password")
    return user
