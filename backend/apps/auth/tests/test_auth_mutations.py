import pytest
from django.test import Client


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
