import uuid
from typing import cast

import pytest
from django.test import Client

from apps.content.models import ContentPiece

CREATE_CAMPAIGN_MUTATION = """
    mutation {
        createCampaign(input: { name: "GraphQL Review Test" }) {
            id
        }
    }
"""


def _create_campaign(client: Client) -> str:
    resp = client.post(
        "/graphql",
        {"query": CREATE_CAMPAIGN_MUTATION},
        content_type="application/json",
    )
    return cast("str", resp.json()["data"]["createCampaign"]["id"])


def _create_content(client: Client, campaign_id: str, headline: str = "Test") -> str:
    resp = client.post(
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
                    "headline": headline,
                    "description": "Desc",
                }
            },
        },
        content_type="application/json",
    )
    return cast("str", resp.json()["data"]["createContentPiece"]["id"])


def _set_state(content_id: str, state: str) -> None:
    piece = ContentPiece.objects.get(id=content_id)
    piece.state = state
    piece.save(update_fields=["state"])


@pytest.mark.django_db
class TestReviewGraphQL:
    def test_approve_content_mutation(self) -> None:
        client = Client()
        campaign_id = _create_campaign(client)
        content_id = _create_content(client, campaign_id)
        _set_state(content_id, ContentPiece.State.SUGGESTED_BY_AI)

        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $action: ReviewAction!) {
                        reviewContent(contentId: $id, action: $action) {
                            id
                            state
                        }
                    }
                """,
                "variables": {"id": content_id, "action": "APPROVE"},
            },
            content_type="application/json",
        )
        data = response.json()
        assert "errors" not in data, str(data.get("errors"))
        assert data["data"]["reviewContent"]["state"] == "APPROVED"

    def test_reject_content_mutation(self) -> None:
        client = Client()
        campaign_id = _create_campaign(client)
        content_id = _create_content(client, campaign_id)
        _set_state(content_id, ContentPiece.State.SUGGESTED_BY_AI)

        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $action: ReviewAction!, $feedback: String) {
                        reviewContent(contentId: $id, action: $action, feedback: $feedback) {
                            id
                            state
                        }
                    }
                """,
                "variables": {"id": content_id, "action": "REJECT", "feedback": "Bad"},
            },
            content_type="application/json",
        )
        data = response.json()
        assert "errors" not in data, str(data.get("errors"))
        assert data["data"]["reviewContent"]["state"] == "REJECTED"

    def test_request_edits_mutation(self) -> None:
        client = Client()
        campaign_id = _create_campaign(client)
        content_id = _create_content(client, campaign_id)
        _set_state(content_id, ContentPiece.State.SUGGESTED_BY_AI)

        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $action: ReviewAction!, $feedback: String) {
                        reviewContent(contentId: $id, action: $action, feedback: $feedback) {
                            id
                            state
                        }
                    }
                """,
                "variables": {
                    "id": content_id,
                    "action": "REQUEST_EDITS",
                    "feedback": "Revise tone",
                },
            },
            content_type="application/json",
        )
        data = response.json()
        assert "errors" not in data, str(data.get("errors"))
        assert data["data"]["reviewContent"]["state"] == "REVIEWED"

    def test_invalid_action_returns_error(self) -> None:
        client = Client()
        campaign_id = _create_campaign(client)
        content_id = _create_content(client, campaign_id)

        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $action: ReviewAction!) {
                        reviewContent(contentId: $id, action: $action) {
                            id
                        }
                    }
                """,
                "variables": {"id": content_id, "action": "APPROVE"},
            },
            content_type="application/json",
        )
        data = response.json()
        assert data.get("errors") is not None
        error_msg = str(data["errors"][0]["message"]).lower()
        assert "cannot transition" in error_msg

    def test_edit_content_mutation(self) -> None:
        client = Client()
        campaign_id = _create_campaign(client)
        content_id = _create_content(client, campaign_id)
        _set_state(content_id, ContentPiece.State.REJECTED)

        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $headline: String!, $description: String, $body: String) {
                        editContent(
                            contentId: $id
                            headline: $headline
                            description: $description
                            body: $body
                        ) {
                            id
                            headline
                            description
                            state
                        }
                    }
                """,
                "variables": {
                    "id": content_id,
                    "headline": "Fixed Headline",
                    "description": "Fixed description",
                    "body": "Fixed body",
                },
            },
            content_type="application/json",
        )
        data = response.json()
        assert "errors" not in data, str(data.get("errors"))
        result = data["data"]["editContent"]
        assert result["headline"] == "Fixed Headline"
        assert result["description"] == "Fixed description"
        assert result["state"] == "DRAFT"

    def test_edit_content_invalid_id(self) -> None:
        client = Client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $headline: String!) {
                        editContent(contentId: $id, headline: $headline) { id }
                    }
                """,
                "variables": {"id": str(uuid.uuid4()), "headline": "Nope"},
            },
            content_type="application/json",
        )
        data = response.json()
        assert "errors" not in data, str(data.get("errors"))
        assert data["data"]["editContent"] is None

    def test_review_content_invalid_id_returns_error(self) -> None:
        client = Client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $action: ReviewAction!) {
                        reviewContent(contentId: $id, action: $action) {
                            id
                        }
                    }
                """,
                "variables": {"id": str(uuid.uuid4()), "action": "APPROVE"},
            },
            content_type="application/json",
        )
        data = response.json()
        assert "errors" not in data, str(data.get("errors"))
        assert data["data"]["reviewContent"] is None
