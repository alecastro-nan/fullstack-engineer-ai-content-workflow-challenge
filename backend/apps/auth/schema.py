import strawberry
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from graphql import GraphQLError

from apps.auth.exceptions import AuthError, InvalidCredentials
from apps.auth.rate_limit import RateLimitError, check_rate_limit
from apps.auth.services import (
    create_tokens,
    login_user,
    refresh_tokens,
    register_user,
)


@strawberry.type
class UserType:
    id: strawberry.ID
    email: str
    created_at: str


@strawberry.type
class AuthPayload:
    user: UserType
    access_token: str
    refresh_token: str


@strawberry.type
class TokenPayload:
    access_token: str
    refresh_token: str


def _user_to_type(user: User) -> UserType:
    return UserType(
        id=strawberry.ID(str(user.id)),
        email=str(user.email),
        created_at=str(user.date_joined.isoformat()),
    )


@strawberry.type
class AuthMutation:
    @strawberry.mutation
    def register_user(self, info: strawberry.types.Info, email: str, password: str) -> AuthPayload:
        check_rate_limit("register", 1, 60, info.context.request)
        try:
            user = register_user(email, password)
        except (InvalidCredentials, ValidationError) as e:
            raise GraphQLError(str(e)) from e
        except RateLimitError as e:
            raise GraphQLError(str(e)) from e
        tokens = create_tokens(user)
        return AuthPayload(
            user=_user_to_type(user),
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )

    @strawberry.mutation
    def login(self, info: strawberry.types.Info, email: str, password: str) -> AuthPayload:
        check_rate_limit("login", 10, 60, info.context.request)
        try:
            user = login_user(email, password)
        except InvalidCredentials as e:
            raise GraphQLError(str(e)) from e
        except RateLimitError as e:
            raise GraphQLError(str(e)) from e
        tokens = create_tokens(user)
        return AuthPayload(
            user=_user_to_type(user),
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )

    @strawberry.mutation
    def refresh_token(self, info: strawberry.types.Info, refresh_token: str) -> TokenPayload:
        check_rate_limit("refresh", 20, 60, info.context.request)
        try:
            tokens = refresh_tokens(refresh_token)
        except (AuthError, Exception) as e:
            raise GraphQLError(str(e)) from e
        except RateLimitError as e:
            raise GraphQLError(str(e)) from e
        return TokenPayload(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )
