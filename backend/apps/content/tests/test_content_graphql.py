from typing import cast

import pytest
from django.test import Client

CREATE_CAMPAIGN_MUTATION = """
    mutation {
        createCampaign(input: { name: "Content Test Campaign" }) {
            id
        }
    }
"""


@pytest.mark.django_db
class TestContentPieceGraphQL:
    def _create_campaign(self, client: Client) -> str:
        resp = client.post(
            "/graphql",
            {"query": CREATE_CAMPAIGN_MUTATION},
            content_type="application/json",
        )
        return cast(str, resp.json()["data"]["createCampaign"]["id"])

    def test_create_content_mutation(self) -> None:
        client = Client()
        campaign_id = self._create_campaign(client)
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($input: ContentPieceInput!) {
                        createContentPiece(input: $input) {
                            id
                            headline
                            description
                            body
                            language
                            state
                            campaignId
                        }
                    }
                """,
                "variables": {
                    "input": {
                        "campaignId": campaign_id,
                        "headline": "Test Headline",
                        "description": "Desc",
                        "body": "Body",
                        "language": "en",
                    }
                },
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["createContentPiece"]["headline"] == "Test Headline"
        assert data["data"]["createContentPiece"]["description"] == "Desc"
        assert data["data"]["createContentPiece"]["body"] == "Body"
        assert data["data"]["createContentPiece"]["language"] == "en"
        assert data["data"]["createContentPiece"]["state"] == "DRAFT"
        assert data["data"]["createContentPiece"]["campaignId"] == campaign_id

    def test_create_content_empty_headline(self) -> None:
        client = Client()
        campaign_id = self._create_campaign(client)
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($input: ContentPieceInput!) {
                        createContentPiece(input: $input) {
                            id
                        }
                    }
                """,
                "variables": {
                    "input": {
                        "campaignId": campaign_id,
                        "headline": "",
                    }
                },
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is not None

    def test_create_content_nonexistent_campaign(self) -> None:
        client = Client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($input: ContentPieceInput!) {
                        createContentPiece(input: $input) {
                            id
                        }
                    }
                """,
                "variables": {
                    "input": {
                        "campaignId": "00000000-0000-0000-0000-000000000000",
                        "headline": "Orphan",
                    }
                },
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is not None

    def test_create_content_invalid_campaign_id(self) -> None:
        client = Client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($input: ContentPieceInput!) {
                        createContentPiece(input: $input) {
                            id
                        }
                    }
                """,
                "variables": {
                    "input": {
                        "campaignId": "not-a-uuid",
                        "headline": "Invalid",
                    }
                },
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is not None

    def test_content_pieces_query(self) -> None:
        client = Client()
        campaign_id = self._create_campaign(client)
        client.post(
            "/graphql",
            {
                "query": """
                    mutation($input: ContentPieceInput!) {
                        createContentPiece(input: $input) { id }
                    }
                """,
                "variables": {
                    "input": {"campaignId": campaign_id, "headline": "Piece A"}
                },
            },
            content_type="application/json",
        )
        client.post(
            "/graphql",
            {
                "query": """
                    mutation($input: ContentPieceInput!) {
                        createContentPiece(input: $input) { id }
                    }
                """,
                "variables": {
                    "input": {"campaignId": campaign_id, "headline": "Piece B"}
                },
            },
            content_type="application/json",
        )
        response = client.post(
            "/graphql",
            {
                "query": """
                    query($campaignId: ID) {
                        contentPieces(campaignId: $campaignId, page: 1, perPage: 10) {
                            totalCount
                            items { id headline }
                        }
                    }
                """,
                "variables": {"campaignId": campaign_id},
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["contentPieces"]["totalCount"] >= 2
        headlines = [e["headline"] for e in data["data"]["contentPieces"]["items"]]
        assert "Piece A" in headlines
        assert "Piece B" in headlines

    def test_content_piece_query_by_id(self) -> None:
        client = Client()
        campaign_id = self._create_campaign(client)
        create_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation($input: ContentPieceInput!) {
                        createContentPiece(input: $input) { id headline }
                    }
                """,
                "variables": {
                    "input": {
                        "campaignId": campaign_id,
                        "headline": "Findable",
                        "description": "Find me",
                    }
                },
            },
            content_type="application/json",
        )
        piece_id = create_resp.json()["data"]["createContentPiece"]["id"]
        response = client.post(
            "/graphql",
            {
                "query": """
                    query($id: ID!) {
                        contentPiece(id: $id) {
                            id
                            headline
                            description
                        }
                    }
                """,
                "variables": {"id": piece_id},
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["contentPiece"]["headline"] == "Findable"
        assert data["data"]["contentPiece"]["description"] == "Find me"

    def test_content_piece_query_not_found(self) -> None:
        client = Client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    query {
                        contentPiece(id: "00000000-0000-0000-0000-000000000000") {
                            id
                        }
                    }
                """
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["contentPiece"] is None

    def test_update_content_mutation(self) -> None:
        client = Client()
        campaign_id = self._create_campaign(client)
        create_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation($input: ContentPieceInput!) {
                        createContentPiece(input: $input) { id }
                    }
                """,
                "variables": {
                    "input": {"campaignId": campaign_id, "headline": "Original"}
                },
            },
            content_type="application/json",
        )
        piece_id = create_resp.json()["data"]["createContentPiece"]["id"]
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $input: ContentPieceUpdateInput!) {
                        updateContentPiece(id: $id, input: $input) {
                            id
                            headline
                            description
                        }
                    }
                """,
                "variables": {
                    "id": piece_id,
                    "input": {"headline": "Updated", "description": "New desc"},
                },
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updateContentPiece"]["headline"] == "Updated"
        assert data["data"]["updateContentPiece"]["description"] == "New desc"

    def test_update_content_not_found(self) -> None:
        client = Client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $input: ContentPieceUpdateInput!) {
                        updateContentPiece(id: $id, input: $input) {
                            id
                        }
                    }
                """,
                "variables": {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "input": {"headline": "Ghost"},
                },
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updateContentPiece"] is None

    def test_update_content_invalid_id(self) -> None:
        client = Client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($input: ContentPieceUpdateInput!) {
                        updateContentPiece(id: "not-a-uuid", input: $input) {
                            id
                        }
                    }
                """,
                "variables": {"input": {"headline": "Nope"}},
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is not None

    def test_delete_content_mutation(self) -> None:
        client = Client()
        campaign_id = self._create_campaign(client)
        create_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation($input: ContentPieceInput!) {
                        createContentPiece(input: $input) { id }
                    }
                """,
                "variables": {
                    "input": {"campaignId": campaign_id, "headline": "Delete Me"}
                },
            },
            content_type="application/json",
        )
        piece_id = create_resp.json()["data"]["createContentPiece"]["id"]
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        deleteContentPiece(id: $id)
                    }
                """,
                "variables": {"id": piece_id},
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteContentPiece"] is True
        verify = client.post(
            "/graphql",
            {
                "query": """
                    query($id: ID!) {
                        contentPiece(id: $id) {
                            id
                        }
                    }
                """,
                "variables": {"id": piece_id},
            },
            content_type="application/json",
        )
        assert verify.json()["data"]["contentPiece"] is None

    def test_delete_content_invalid_id(self) -> None:
        client = Client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        deleteContentPiece(id: "not-a-uuid")
                    }
                """
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is not None
