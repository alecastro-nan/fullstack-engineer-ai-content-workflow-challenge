import uuid

import pytest

from apps.auth.test_utils import make_auth_client


@pytest.mark.django_db
class TestContentGraphQL:
    def test_create_content_piece(self) -> None:
        client = make_auth_client()
        create_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        createCampaign(input: { name: "C1" }) { id }
                    }
                """
            },
            content_type="application/json",
        )
        campaign_id = create_resp.json()["data"]["createCampaign"]["id"]

        resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation($input: ContentPieceInput!) {
                        createContentPiece(input: $input) {
                            id
                            headline
                            state
                            campaignId
                        }
                    }
                """,
                "variables": {
                    "input": {
                        "campaignId": campaign_id,
                        "headline": "Test Headline",
                        "description": "Test Description",
                    }
                },
            },
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["createContentPiece"]["headline"] == "Test Headline"
        assert data["data"]["createContentPiece"]["state"] == "DRAFT"

    def test_create_content_piece_empty_headline(self) -> None:
        client = make_auth_client()
        create_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        createCampaign(input: { name: "C2" }) { id }
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
        assert response.json().get("errors") is not None

    def test_create_content_piece_invalid_campaign(self) -> None:
        client = make_auth_client()
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
        assert response.json().get("errors") is not None

    def test_content_pieces_query(self) -> None:
        client = make_auth_client()
        create_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        createCampaign(input: { name: "C3" }) { id }
                    }
                """
            },
            content_type="application/json",
        )
        campaign_id = create_resp.json()["data"]["createCampaign"]["id"]

        client.post(
            "/graphql",
            {
                "query": """
                    mutation($input: ContentPieceInput!) {
                        createContentPiece(input: $input) { id }
                    }
                """,
                "variables": {
                    "input": {
                        "campaignId": campaign_id,
                        "headline": "CP1",
                    }
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
                    "input": {
                        "campaignId": campaign_id,
                        "headline": "CP2",
                    }
                },
            },
            content_type="application/json",
        )
        response = client.post(
            "/graphql",
            {
                "query": """
                    query($campaignId: ID) {
                        contentPieces(campaignId: $campaignId) {
                            totalCount
                            items { headline }
                        }
                    }
                """,
                "variables": {"campaignId": campaign_id},
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["contentPieces"]["totalCount"] >= 2
        headlines = [i["headline"] for i in data["contentPieces"]["items"]]
        assert "CP1" in headlines

    def test_content_piece_query_by_id(self) -> None:
        client = make_auth_client()
        create_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        createCampaign(input: { name: "C4" }) { id }
                    }
                """
            },
            content_type="application/json",
        )
        campaign_id = create_resp.json()["data"]["createCampaign"]["id"]

        content_resp = client.post(
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
                        "headline": "Findable Content",
                    }
                },
            },
            content_type="application/json",
        )
        content_id = content_resp.json()["data"]["createContentPiece"]["id"]

        response = client.post(
            "/graphql",
            {
                "query": """
                    query($id: ID!) {
                        contentPiece(id: $id) {
                            id
                            headline
                            campaignId
                        }
                    }
                """,
                "variables": {"id": content_id},
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()["data"]["contentPiece"]
        assert data["headline"] == "Findable Content"

    def test_content_piece_not_found(self) -> None:
        client = make_auth_client()
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

    def test_update_content_piece(self) -> None:
        client = make_auth_client()
        create_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        createCampaign(input: { name: "C5" }) { id }
                    }
                """
            },
            content_type="application/json",
        )
        campaign_id = create_resp.json()["data"]["createCampaign"]["id"]

        content_resp = client.post(
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
                        "headline": "Original",
                    }
                },
            },
            content_type="application/json",
        )
        content_id = content_resp.json()["data"]["createContentPiece"]["id"]

        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $input: ContentPieceUpdateInput!) {
                        updateContentPiece(id: $id, input: $input) {
                            id
                            headline
                            description
                            language
                        }
                    }
                """,
                "variables": {
                    "id": content_id,
                    "input": {
                        "headline": "Updated",
                        "description": "New Desc",
                    },
                },
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()["data"]["updateContentPiece"]
        assert data["headline"] == "Updated"
        assert data["description"] == "New Desc"

    def test_delete_content_piece(self) -> None:
        client = make_auth_client()
        create_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        createCampaign(input: { name: "C6" }) { id }
                    }
                """
            },
            content_type="application/json",
        )
        campaign_id = create_resp.json()["data"]["createCampaign"]["id"]

        content_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation($input: ContentPieceInput!) {
                        createContentPiece(input: $input) { id }
                    }
                """,
                "variables": {
                    "input": {
                        "campaignId": campaign_id,
                        "headline": "Delete Me",
                    }
                },
            },
            content_type="application/json",
        )
        content_id = content_resp.json()["data"]["createContentPiece"]["id"]

        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        deleteContentPiece(id: $id)
                    }
                """,
                "variables": {"id": content_id},
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["data"]["deleteContentPiece"] is True

        verify = client.post(
            "/graphql",
            {
                "query": """
                    query($id: ID!) {
                        contentPiece(id: $id) { id }
                    }
                """,
                "variables": {"id": content_id},
            },
            content_type="application/json",
        )
        assert verify.json()["data"]["contentPiece"] is None

    def test_update_content_piece_not_found(self) -> None:
        client = make_auth_client()
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
                    "id": str(uuid.uuid4()),
                    "input": {"headline": "Ghost"},
                },
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["data"]["updateContentPiece"] is None

    def test_delete_content_piece_not_found(self) -> None:
        client = make_auth_client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        deleteContentPiece(id: "00000000-0000-0000-0000-000000000000")
                    }
                """
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deleteContentPiece"] is False

    def test_create_content_piece_with_language(self) -> None:
        client = make_auth_client()
        create_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        createCampaign(input: { name: "C7" }) { id }
                    }
                """
            },
            content_type="application/json",
        )
        campaign_id = create_resp.json()["data"]["createCampaign"]["id"]

        resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation($input: ContentPieceInput!) {
                        createContentPiece(input: $input) {
                            id
                            language
                        }
                    }
                """,
                "variables": {
                    "input": {
                        "campaignId": campaign_id,
                        "headline": "Hola",
                        "language": "es",
                    }
                },
            },
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["createContentPiece"]["language"] == "es"
