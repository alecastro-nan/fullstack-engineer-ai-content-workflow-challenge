import jwt
import pytest
from django.contrib.auth.models import User
from django.test import Client, override_settings

from apps.auth.exceptions import InvalidToken
from apps.auth.services import (
    _get_jwt_secret,
    create_access_token,
    create_tokens,
    decode_token,
    invalidate_user_tokens,
    refresh_tokens,
)


@pytest.mark.django_db
class TestAuthMutations:
    def test_register_user(self) -> None:
        client = Client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        registerUser(email: "new@test.com", password: "testpass123") {
                            user { id email }
                            accessToken
                            refreshToken
                        }
                    }
                """
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()["data"]["registerUser"]
        assert data["user"]["email"] == "new@test.com"
        assert data["accessToken"] is not None
        assert data["refreshToken"] is not None

    def test_register_duplicate_email(self) -> None:
        client = Client()
        client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        registerUser(email: "dup@test.com", password: "testpass123") {
                            user { id }
                        }
                    }
                """
            },
            content_type="application/json",
        )
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        registerUser(email: "dup@test.com", password: "testpass123") {
                            user { id }
                        }
                    }
                """
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json().get("errors") is not None

    def test_login_valid(self) -> None:
        register_client = Client()
        register_client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        registerUser(email: "login@test.com", password: "testpass123") {
                            user { id }
                        }
                    }
                """
            },
            content_type="application/json",
        )
        client = Client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        login(email: "login@test.com", password: "testpass123") {
                            user { email }
                            accessToken
                            refreshToken
                        }
                    }
                """
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()["data"]["login"]
        assert data["user"]["email"] == "login@test.com"
        assert data["accessToken"] is not None

    def test_login_invalid_password(self) -> None:
        client = Client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        login(email: "nonexist@test.com", password: "wrong") {
                            user { id }
                        }
                    }
                """
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json().get("errors") is not None

    def test_refresh_token_valid(self) -> None:
        client = Client()
        reg_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        registerUser(email: "refresh@test.com", password: "testpass123") {
                            refreshToken
                        }
                    }
                """
            },
            content_type="application/json",
        )
        refresh_token = reg_resp.json()["data"]["registerUser"]["refreshToken"]

        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($token: String!) {
                        refreshToken(refreshToken: $token) {
                            accessToken
                        }
                    }
                """,
                "variables": {"token": refresh_token},
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["data"]["refreshToken"]["accessToken"] is not None

    def test_mutation_needs_auth(self) -> None:
        client = Client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        createCampaign(input: { name: "Hack" }) {
                            id
                        }
                    }
                """
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is not None
        assert "Authentication required" in str(data["errors"])

    def test_health_does_not_need_auth(self) -> None:
        client = Client()
        response = client.post(
            "/graphql",
            {
                "query": "{ health }"
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["health"] == "ok"

    def test_ping_does_not_need_auth(self) -> None:
        client = Client()
        response = client.post(
            "/graphql",
            {
                "query": "mutation { ping }"
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["ping"] == "pong"

    def test_invalid_token_format(self) -> None:
        client = Client()
        client.defaults["HTTP_AUTHORIZATION"] = "Bearer invalid-token-format"
        response = client.post(
            "/graphql",
            {
                "query": "{ health }"
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["health"] == "ok"

    def test_refresh_token_returns_both_tokens(self) -> None:
        client = Client()
        reg_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        registerUser(email: "refresh-rotate@test.com", password: "testpass123") {
                            refreshToken
                        }
                    }
                """
            },
            content_type="application/json",
        )
        refresh_token = reg_resp.json()["data"]["registerUser"]["refreshToken"]

        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($token: String!) {
                        refreshToken(refreshToken: $token) {
                            accessToken
                            refreshToken
                        }
                    }
                """,
                "variables": {"token": refresh_token},
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()["data"]["refreshToken"]
        assert data["accessToken"] is not None
        assert data["refreshToken"] is not None

    def test_generic_error_on_duplicate_email(self) -> None:
        client = Client()
        client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        registerUser(email: "dup-error@test.com", password: "testpass123") {
                            user { id }
                        }
                    }
                """
            },
            content_type="application/json",
        )
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        registerUser(email: "dup-error@test.com", password: "testpass123") {
                            user { id }
                        }
                    }
                """
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        errors = response.json().get("errors")
        assert errors is not None
        assert "Email already registered" not in str(errors)
        assert "Registration failed" in str(errors[0]["message"])


@pytest.mark.django_db
class TestTokenVersion:
    def test_token_version_in_payload(self) -> None:
        user = User.objects.create_user(
            username="tv", email="tv@test.com", password="pass1234",
        )
        token = create_access_token(user)
        payload = jwt.decode(token, _get_jwt_secret(), algorithms=["HS256"])
        assert "token_version" in payload
        assert payload["token_version"] == 0

    def test_token_version_validation_passes(self) -> None:
        user = User.objects.create_user(
            username="tv2", email="tv2@test.com", password="pass1234",
        )
        token = create_access_token(user)
        decoded = decode_token(token)
        assert decoded == user

    def test_token_version_validation_fails_after_invalidation(self) -> None:
        user = User.objects.create_user(
            username="tv3", email="tv3@test.com", password="pass1234",
        )
        token = create_access_token(user)
        invalidate_user_tokens(user)
        with pytest.raises(InvalidToken, match="has been invalidated"):
            decode_token(token)

    def test_refresh_token_invalidated_after_version_bump(self) -> None:
        user = User.objects.create_user(
            username="tv4", email="tv4@test.com", password="pass1234",
        )
        tokens = create_tokens(user)
        invalidate_user_tokens(user)
        with pytest.raises(InvalidToken, match="has been invalidated"):
            refresh_tokens(tokens["refresh_token"])

    @override_settings(JWT_SIGNING_KEY="separate-jwt-key-for-testing")
    def test_jwt_signing_key_is_respected(self) -> None:
        User.objects.create_user(
            username="jwtkey", email="jwtkey@test.com", password="pass1234",
        )
        secret = _get_jwt_secret()
        assert secret == "separate-jwt-key-for-testing"

    def test_email_not_in_token_payload(self) -> None:
        user = User.objects.create_user(
            username="noemail", email="noemail@test.com", password="pass1234",
        )
        token = create_access_token(user)
        payload = jwt.decode(token, _get_jwt_secret(), algorithms=["HS256"])
        assert "email" not in payload
