from django.test import Client


class TestHealthEndpoint:
    def test_graphql_health_query(self) -> None:
        client = Client()
        response = client.post(
            "/graphql",
            {"query": "{ health }"},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["health"] == "ok"

    def test_graphql_ping_mutation(self) -> None:
        client = Client()
        response = client.post(
            "/graphql",
            {"query": "mutation { ping }"},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["ping"] == "pong"
