import strawberry
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from graphql import GraphQLError

from apps.auth.exceptions import AuthError, EmailAlreadyRegistered, InvalidCredentials
from apps.auth.services import (
    create_tokens,
    login_user,
    refresh_access_token,
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


def _user_to_type(user: User) -> UserType:
    return UserType(
        id=strawberry.ID(str(user.id)),
        email=str(user.email),
        created_at=str(user.date_joined.isoformat()),
    )


@strawberry.type
class AuthMutation:
    @strawberry.mutation
    def register_user(self, email: str, password: str) -> AuthPayload:
        try:
            user = register_user(email, password)
        except EmailAlreadyRegistered as e:
            raise GraphQLError(str(e)) from e
        except (InvalidCredentials, ValidationError) as e:
            raise GraphQLError(str(e)) from e
        tokens = create_tokens(user)
        return AuthPayload(
            user=_user_to_type(user),
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )

    @strawberry.mutation
    def login(self, email: str, password: str) -> AuthPayload:
        try:
            user = login_user(email, password)
        except InvalidCredentials as e:
            raise GraphQLError(str(e)) from e
        tokens = create_tokens(user)
        return AuthPayload(
            user=_user_to_type(user),
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )

    @strawberry.mutation
    def refresh_token(self, refresh_token: str) -> TokenPayload:
        try:
            access_token = refresh_access_token(refresh_token)
        except (AuthError, Exception) as e:
            raise GraphQLError(str(e)) from e
        return TokenPayload(access_token=access_token)
