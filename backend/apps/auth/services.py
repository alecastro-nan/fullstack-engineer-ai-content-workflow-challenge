from datetime import UTC, datetime, timedelta
from typing import cast

import jwt
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from apps.auth.exceptions import EmailAlreadyRegistered, InvalidCredentials, InvalidToken

ACCESS_TOKEN_EXPIRY_MINUTES = 15
REFRESH_TOKEN_EXPIRY_DAYS = 7


def _get_jwt_secret() -> str:
    return cast(str, settings.SECRET_KEY)


def _now() -> datetime:
    return datetime.now(tz=UTC)


def create_access_token(user: User) -> str:
    payload = {
        "user_id": user.pk,
        "email": user.email,
        "type": "access",
        "exp": _now() + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES),
        "iat": _now(),
    }
    return jwt.encode(payload, _get_jwt_secret(), algorithm="HS256")


def create_refresh_token(user: User) -> str:
    payload = {
        "user_id": user.pk,
        "email": user.email,
        "type": "refresh",
        "exp": _now() + timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS),
        "iat": _now(),
    }
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
        return User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        raise InvalidToken("User not found") from None


async def decode_token_async(token: str) -> User | None:
    try:
        return await sync_to_async(decode_token)(token)
    except InvalidToken:
        return None


def refresh_access_token(refresh_token: str) -> str:
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
    return create_access_token(user)


def register_user(email: str, password: str) -> User:
    if User.objects.filter(email=email).exists():
        raise EmailAlreadyRegistered("Email already registered")
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
    return cast(User, user)
