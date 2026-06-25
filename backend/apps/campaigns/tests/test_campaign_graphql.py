import pytest

from apps.auth.test_utils import make_auth_client


@pytest.mark.django_db
class TestCampaignGraphQL:
    def test_create_campaign_mutation(self) -> None:
        client = make_auth_client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        createCampaign(input: { name: "My Campaign", description: "Desc" }) {
                            id
                            name
                            description
                            status
                        }
                    }
                """
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["createCampaign"]["name"] == "My Campaign"
        assert data["data"]["createCampaign"]["description"] == "Desc"
        assert data["data"]["createCampaign"]["status"] == "ACTIVE"
        assert data["data"]["createCampaign"]["id"] is not None

    def test_create_campaign_mutation_empty_name(self) -> None:
        client = make_auth_client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        createCampaign(input: { name: "" }) {
                            id
                            name
                        }
                    }
                """
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is not None

    def test_campaigns_query(self) -> None:
        client = make_auth_client()
        client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        createCampaign(input: { name: "A" }) { id }
                    }
                """
            },
            content_type="application/json",
        )
        client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        createCampaign(input: { name: "B" }) { id }
                    }
                """
            },
            content_type="application/json",
        )
        response = client.post(
            "/graphql",
            {
                "query": """
                    query {
                        campaigns(page: 1, perPage: 10) {
                            totalCount
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
        data = response.json()
        assert data["data"]["campaigns"]["totalCount"] >= 2
        names = [e["name"] for e in data["data"]["campaigns"]["items"]]
        assert "A" in names
        assert "B" in names

    def test_campaign_query_by_id(self) -> None:
        client = make_auth_client()
        create_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        createCampaign(input: { name: "Findable", description: "Find me" }) {
                            id
                            name
                        }
                    }
                """
            },
            content_type="application/json",
        )
        campaign_id = create_resp.json()["data"]["createCampaign"]["id"]
        response = client.post(
            "/graphql",
            {
                "query": """
                    query($id: ID!) {
                        campaign(id: $id) {
                            id
                            name
                            description
                        }
                    }
                """,
                "variables": {"id": campaign_id},
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["campaign"]["name"] == "Findable"
        assert data["data"]["campaign"]["description"] == "Find me"

    def test_campaign_query_not_found(self) -> None:
        client = make_auth_client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    query {
                        campaign(id: "00000000-0000-0000-0000-000000000000") {
                            id
                            name
                        }
                    }
                """
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["campaign"] is None

    def test_update_campaign_mutation(self) -> None:
        client = make_auth_client()
        create_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        createCampaign(input: { name: "Original" }) {
                            id
                        }
                    }
                """
            },
            content_type="application/json",
        )
        campaign_id = create_resp.json()["data"]["createCampaign"]["id"]
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        updateCampaign(id: $id, input: { name: "Updated" }) {
                            id
                            name
                        }
                    }
                """,
                "variables": {"id": campaign_id},
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updateCampaign"]["name"] == "Updated"

    def test_update_campaign_not_found(self) -> None:
        client = make_auth_client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        updateCampaign(id: $id, input: { name: "Ghost" }) {
                            id
                            name
                        }
                    }
                """,
                "variables": {"id": "00000000-0000-0000-0000-000000000000"},
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updateCampaign"] is None

    def test_update_campaign_invalid_id(self) -> None:
        client = make_auth_client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        updateCampaign(
                            id: "not-a-uuid",
                            input: { name: "Nope" }
                        ) {
                            id
                            name
                        }
                    }
                """
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updateCampaign"] is None

    def test_delete_campaign_mutation(self) -> None:
        client = make_auth_client()
        create_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        createCampaign(input: { name: "Delete Me" }) {
                            id
                        }
                    }
                """
            },
            content_type="application/json",
        )
        campaign_id = create_resp.json()["data"]["createCampaign"]["id"]
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        deleteCampaign(id: $id)
                    }
                """,
                "variables": {"id": campaign_id},
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteCampaign"] is True
        verify = client.post(
            "/graphql",
            {
                "query": """
                    query($id: ID!) {
                        campaign(id: $id) {
                            id
                            name
                        }
                    }
                """,
                "variables": {"id": campaign_id},
            },
            content_type="application/json",
        )
        assert verify.json()["data"]["campaign"] is None

    def test_delete_campaign_invalid_id(self) -> None:
        client = make_auth_client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        deleteCampaign(id: "not-a-uuid")
                    }
                """
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteCampaign"] is False
