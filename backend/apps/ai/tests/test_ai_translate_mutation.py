import json
import uuid
from typing import cast
from unittest.mock import MagicMock, patch

from django.test import Client, TestCase, override_settings

from apps.auth.test_utils import make_auth_client
from apps.content.models import ContentPiece
from apps.reviews.enums import ReviewAction
from apps.reviews.models import StateHistory


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
            "variables": {"name": "Translate Test Campaign", "description": "For translate tests"},
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
                    "headline": "Original Headline",
                    "description": "Original description for testing translation.",
                    "body": "Original body content for translation.",
                }
            },
        },
        content_type="application/json",
    )
    return cast("str", response.json()["data"]["createContentPiece"]["id"])


@override_settings(
    AI_PROVIDER="openai",
    OPENAI_API_KEY="sk-test-invalid-key-do-not-use",
    ANTHROPIC_API_KEY="",
)
class TestAiTranslateMutation(TestCase):
    def setUp(self) -> None:
        self.client = make_auth_client()

    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_translate_content_success(self, mock_openai: MagicMock) -> None:
        mock_instance = mock_openai.return_value
        mock_choice = mock_instance.chat.completions.create.return_value.choices[0]
        mock_choice.message.content = json.dumps(
            {"headline": "Título traducido", "description": "Descripción traducida."}
        )

        campaign_id = _create_campaign(self.client)
        content_id = _create_content(self.client, campaign_id)

        response = self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $lang: String!) {
                        translateContent(contentId: $id, targetLanguage: $lang) {
                            id
                            headline
                            description
                            state
                            language
                            originalId
                        }
                    }
                """,
                "variables": {"id": content_id, "lang": "es"},
            },
            content_type="application/json",
        )
        data = response.json()
        assert "errors" not in data, str(data.get("errors"))
        result = data["data"]["translateContent"]
        assert result["headline"] == "Título traducido"
        assert result["description"] == "Descripción traducida."
        assert result["state"] == "SUGGESTED_BY_AI"
        assert result["language"] == "es"
        assert result["originalId"] == content_id

        # Verify new piece has different ID
        assert result["id"] != content_id

        translated = ContentPiece.objects.get(id=result["id"])
        assert translated.original_id == uuid.UUID(content_id)  # type: ignore[attr-defined]
        assert translated.state == ContentPiece.State.SUGGESTED_BY_AI
        assert translated.language == "es"
        assert translated.body == "Original body content for translation."

        history = StateHistory.objects.filter(content_piece_id=result["id"]).first()
        assert history is not None
        assert history.from_state == ContentPiece.State.DRAFT
        assert history.to_state == ContentPiece.State.SUGGESTED_BY_AI
        assert history.action == ReviewAction.GENERATE_AI.value

    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_translate_content_nonexistent(self, mock_openai: MagicMock) -> None:
        response = self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $lang: String!) {
                        translateContent(contentId: $id, targetLanguage: $lang) {
                            id
                        }
                    }
                """,
                "variables": {"id": "00000000-0000-0000-0000-000000000000", "lang": "es"},
            },
            content_type="application/json",
        )
        data = response.json()
        assert data["data"]["translateContent"] is None

    def test_translate_content_unsupported_language(self) -> None:
        campaign_id = _create_campaign(self.client)
        content_id = _create_content(self.client, campaign_id)

        response = self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $lang: String!) {
                        translateContent(contentId: $id, targetLanguage: $lang) {
                            id
                        }
                    }
                """,
                "variables": {"id": content_id, "lang": "xh"},
            },
            content_type="application/json",
        )
        data = response.json()
        assert data.get("errors") is not None
        assert "Unsupported language" in str(data["errors"])

    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_translate_content_ai_failure(self, mock_openai: MagicMock) -> None:
        mock_openai.return_value.chat.completions.create.side_effect = Exception(
            "Translation API error"
        )

        campaign_id = _create_campaign(self.client)
        content_id = _create_content(self.client, campaign_id)

        response = self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $lang: String!) {
                        translateContent(contentId: $id, targetLanguage: $lang) {
                            id
                        }
                    }
                """,
                "variables": {"id": content_id, "lang": "fr"},
            },
            content_type="application/json",
        )
        data = response.json()
        assert data.get("errors") is not None
        assert "AI translation failed" in str(data["errors"])

    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_translate_content_malformed_response(self, mock_openai: MagicMock) -> None:
        mock_instance = mock_openai.return_value
        mock_choice = mock_instance.chat.completions.create.return_value.choices[0]
        mock_choice.message.content = "not valid json"

        campaign_id = _create_campaign(self.client)
        content_id = _create_content(self.client, campaign_id)

        response = self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $lang: String!) {
                        translateContent(contentId: $id, targetLanguage: $lang) {
                            id
                        }
                    }
                """,
                "variables": {"id": content_id, "lang": "de"},
            },
            content_type="application/json",
        )
        data = response.json()
        assert data.get("errors") is not None
        assert "AI translation failed" in str(data["errors"])

    def test_translate_content_invalid_id(self) -> None:
        response = self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $lang: String!) {
                        translateContent(contentId: $id, targetLanguage: $lang) {
                            id
                        }
                    }
                """,
                "variables": {"id": "not-a-uuid", "lang": "es"},
            },
            content_type="application/json",
        )
        data = response.json()
        assert data.get("errors") is not None
        assert "Invalid content piece ID" in str(data["errors"])
