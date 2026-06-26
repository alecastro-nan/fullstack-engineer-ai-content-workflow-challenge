from django.test import Client, TestCase, override_settings


class TestGraphQLLimits(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_reasonable_query_passes_depth_limit(self) -> None:
        response = self.client.post(
            "/graphql",
            {
                "query": """
                    query {
                        campaigns {
                            items {
                                id
                                name
                            }
                        }
                    }
                """
            },
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_max_aliases_exceeded(self) -> None:
        query = """
            query {
                a1: health
                a2: health
                a3: health
                a4: health
                a5: health
                a6: health
            }
        """
        response = self.client.post(
            "/graphql",
            {"query": query},
            content_type="application/json",
        )
        data = response.json()
        assert data.get("errors") is not None
        error_msg = str(data["errors"]).lower()
        assert "alias" in error_msg

    def test_large_query_exceeds_token_limit(self) -> None:
        many_health = " ".join(["health"] * 1000)
        query = f"query {{ health {many_health} }}"
        response = self.client.post(
            "/graphql",
            {"query": query},
            content_type="application/json",
        )
        data = response.json()
        assert data.get("errors") is not None
        error_msg = str(data["errors"]).lower()
        assert "token" in error_msg or "count" in error_msg or "limit" in error_msg


class TestIntrospectionLogic(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.introspection_query = {
            "query": "query { __schema { types { name } } }"
        }

    @override_settings(DEBUG=True)
    def test_introspection_enabled_when_debug(self) -> None:
        response = self.client.post(
            "/graphql", self.introspection_query, content_type="application/json"
        )
        data = response.json()
        assert "errors" not in data, f"Introspection should work in DEBUG mode: {data}"
        assert data.get("data", {}).get("__schema") is not None

    @override_settings(DEBUG=False)
    def test_introspection_disabled_when_not_debug(self) -> None:
        response = self.client.post(
            "/graphql", self.introspection_query, content_type="application/json"
        )
        data = response.json()
        assert data.get("errors") is not None


class TestAllowedHosts(TestCase):
    @override_settings(ALLOWED_HOSTS=["specific-host.example.com"])
    def test_rejects_invalid_host_header(self) -> None:
        client = Client(SERVER_NAME="evil-attacker.com")
        response = client.get("/graphql")
        assert response.status_code == 400


class TestInputLengthCaps(TestCase):
    @override_settings(
        AI_PROVIDER="openai",
        OPENAI_API_KEY="test-invalid-key",
        ANTHROPIC_API_KEY="",
    )
    def test_description_too_long_rejected_at_content_layer(self) -> None:
        from apps.auth.test_utils import make_auth_client

        client = make_auth_client()

        campaign_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation($name: String!) {
                        createCampaign(input: {name: $name}) { id }
                    }
                """,
                "variables": {"name": "Test Campaign"},
            },
            content_type="application/json",
        )
        campaign_id = campaign_resp.json()["data"]["createCampaign"]["id"]

        content_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation($input: ContentPieceInput!) {
                        createContentPiece(input: $input) { id state }
                    }
                """,
                "variables": {
                    "input": {
                        "campaignId": campaign_id,
                        "headline": "Test",
                        "description": "x" * 5001,
                    }
                },
            },
            content_type="application/json",
        )
        data = content_resp.json()
        assert data.get("errors") is not None
        assert "5000" in str(data["errors"])
