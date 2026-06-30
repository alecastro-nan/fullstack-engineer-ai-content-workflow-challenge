import json
from typing import cast
from unittest.mock import MagicMock, patch

from django.test import Client, TestCase, override_settings

from apps.auth.test_utils import make_auth_client
from apps.content.models import ContentPiece


def _create_campaign(client: Client) -> str:
    response = client.post(
        "/graphql",
        {
            "query": """
                mutation($name: String!, $description: String) {
                    createCampaign(input: {name: $name, description: $description}) {
                        id
                    }
                }
            """,
            "variables": {"name": "AI Test Campaign", "description": "For AI tests"},
        },
        content_type="application/json",
    )
    return cast("str", response.json()["data"]["createCampaign"]["id"])


def _create_content(client: Client, campaign_id: str) -> str:
    response = client.post(
        "/graphql",
        {
            "query": """
                mutation($input: ContentPieceInput!) {
                    createContentPiece(input: $input) {
                        id
                        state
                    }
                }
            """,
                "variables": {
                    "input": {
                        "campaignId": campaign_id,
                        "headline": "Test Content",
                        "description": "Content about AI technology and its impact on society",
                        "body": "",
                    }
                },
        },
        content_type="application/json",
    )
    return cast("str", response.json()["data"]["createContentPiece"]["id"])


@override_settings(
    AI_PROVIDER="openai",
    OPENAI_API_KEY="test-invalid-key",  # Test-only dummy key — not a real credential
    ANTHROPIC_API_KEY="",
)
class TestAiDraftMutation(TestCase):
    def setUp(self) -> None:
        self.client = make_auth_client()

    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_generate_draft_success(self, mock_openai: MagicMock) -> None:
        mock_instance = mock_openai.return_value
        mock_choice = mock_instance.chat.completions.create.return_value.choices[0]
        mock_choice.message.content = json.dumps(
            {"headline": "AI Generated Headline", "description": "AI generated description."}
        )

        campaign_id = _create_campaign(self.client)
        content_id = _create_content(self.client, campaign_id)

        response = self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        generateDraft(contentId: $id) {
                            id
                            headline
                            description
                            state
                        }
                    }
                """,
                "variables": {"id": content_id},
            },
            content_type="application/json",
        )
        data = response.json()
        assert "errors" not in data, str(data.get("errors"))
        result = data["data"]["generateDraft"]
        assert result["headline"] == "AI Generated Headline"
        assert result["description"] == "AI generated description."
        assert result["state"] == "SUGGESTED_BY_AI"

    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_generate_draft_not_in_draft_state(self, mock_openai: MagicMock) -> None:
        campaign_id = _create_campaign(self.client)
        content_id = _create_content(self.client, campaign_id)
        ContentPiece.objects.filter(id=content_id).update(state=ContentPiece.State.APPROVED)

        response = self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        generateDraft(contentId: $id) {
                            id
                            state
                        }
                    }
                """,
                "variables": {"id": content_id},
            },
            content_type="application/json",
        )
        data = response.json()
        assert data.get("errors") is not None
        assert "must be in 'draft' state" in str(data["errors"])

    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_generate_draft_ai_failure_state_preserved(self, mock_openai: MagicMock) -> None:
        mock_openai.return_value.chat.completions.create.side_effect = Exception("API timeout")

        campaign_id = _create_campaign(self.client)
        content_id = _create_content(self.client, campaign_id)

        response = self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        generateDraft(contentId: $id) {
                            id
                            headline
                            description
                            state
                        }
                    }
                """,
                "variables": {"id": content_id},
            },
            content_type="application/json",
        )
        data = response.json()
        assert data.get("errors") is not None
        content = ContentPiece.objects.get(id=content_id)
        assert content.state == ContentPiece.State.DRAFT

    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_generate_draft_malformed_response(self, mock_openai: MagicMock) -> None:
        mock_instance = mock_openai.return_value
        mock_choice = mock_instance.chat.completions.create.return_value.choices[0]
        mock_choice.message.content = "not valid json"

        campaign_id = _create_campaign(self.client)
        content_id = _create_content(self.client, campaign_id)

        response = self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        generateDraft(contentId: $id) {
                            id
                        }
                    }
                """,
                "variables": {"id": content_id},
            },
            content_type="application/json",
        )
        data = response.json()
        assert data.get("errors") is not None
        assert "AI draft generation failed" in str(data["errors"])

    def test_generate_draft_invalid_id(self) -> None:
        response = self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        generateDraft(contentId: $id) {
                            id
                        }
                    }
                """,
                "variables": {"id": "not-a-uuid"},
            },
            content_type="application/json",
        )
        data = response.json()
        assert data.get("errors") is not None

    def test_generate_draft_nonexistent_content(self) -> None:
        response = self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        generateDraft(contentId: $id) {
                            id
                        }
                    }
                """,
                "variables": {"id": "00000000-0000-0000-0000-000000000000"},
            },
            content_type="application/json",
        )
        data = response.json()
        assert data["data"]["generateDraft"] is None
