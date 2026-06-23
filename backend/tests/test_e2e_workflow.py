import json
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

from django.test import Client, TestCase, override_settings

from apps.campaigns.models import Campaign
from apps.content.models import ContentPiece


def _create_campaign(client: Client) -> str:
    response = client.post(
        "/graphql",
        {
            "query": """
                mutation($name: String!, $description: String) {
                    createCampaign(input: {name: $name, description: $description}) {
                        id
                        name
                        status
                    }
                }
            """,
            "variables": {"name": "E2E Workflow Campaign", "description": "Full workflow test"},
        },
        content_type="application/json",
    )
    return cast(str, response.json()["data"]["createCampaign"]["id"])


def _create_content(client: Client, campaign_id: str) -> str:
    response = client.post(
        "/graphql",
        {
            "query": """
                mutation($input: ContentPieceInput!) {
                    createContentPiece(input: $input) {
                        id
                        state
                        headline
                    }
                }
            """,
            "variables": {
                "input": {
                    "campaignId": campaign_id,
                    "headline": "E2E Test Content",
                    "description": "Content for end-to-end workflow test",
                    "body": "Original body text for the E2E test content piece.",
                }
            },
        },
        content_type="application/json",
    )
    return cast(str, response.json()["data"]["createContentPiece"]["id"])


@override_settings(
    AI_PROVIDER="openai",
    OPENAI_API_KEY="sk-test-e2e-key",
    ANTHROPIC_API_KEY="",
)
class TestE2EWorkflow(TestCase):
    """End-to-end test covering the full content workflow.

    Exercises: createCampaign -> createContentPiece -> generateDraft ->
    reviewContent (approve) -> translateContent -> verify results via queries.
    """

    def setUp(self) -> None:
        self.client = Client()

    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_full_workflow_create_to_approve(self, mock_openai: MagicMock) -> None:
        mock_instance = mock_openai.return_value
        mock_choice = mock_instance.chat.completions.create.return_value.choices[0]

        mock_choice.message.content = json.dumps(
            {"headline": "AI Draft Headline", "description": "AI draft description."}
        )

        # Step 1: Create campaign
        campaign_id = _create_campaign(self.client)

        campaign_resp = self.client.post(
            "/graphql",
            {
                "query": """
                    query($id: ID!) {
                        campaign(id: $id) {
                            id
                            name
                            status
                        }
                    }
                """,
                "variables": {"id": campaign_id},
            },
            content_type="application/json",
        )
        campaign_data = campaign_resp.json()
        assert "errors" not in campaign_data, str(campaign_data.get("errors"))
        assert campaign_data["data"]["campaign"]["name"] == "E2E Workflow Campaign"
        assert campaign_data["data"]["campaign"]["status"] == "ACTIVE"

        # Step 2: Create content piece in draft state
        content_id = _create_content(self.client, campaign_id)

        content_resp = self.client.post(
            "/graphql",
            {
                "query": """
                    query($id: ID!) {
                        contentPiece(id: $id) {
                            id
                            state
                            headline
                        }
                    }
                """,
                "variables": {"id": content_id},
            },
            content_type="application/json",
        )
        content_data = content_resp.json()
        assert "errors" not in content_data, str(content_data.get("errors"))
        assert content_data["data"]["contentPiece"]["state"] == "DRAFT"
        assert content_data["data"]["contentPiece"]["headline"] == "E2E Test Content"

        # Step 3: Generate AI draft
        draft_resp = self.client.post(
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
        draft_data = draft_resp.json()
        assert "errors" not in draft_data, str(draft_data.get("errors"))
        draft_result = draft_data["data"]["generateDraft"]
        assert draft_result["state"] == "SUGGESTED_BY_AI"
        assert draft_result["headline"] == "AI Draft Headline"
        assert draft_result["description"] == "AI draft description."

        # Verify content state via query
        state_resp = self.client.post(
            "/graphql",
            {
                "query": """
                    query($id: ID!) {
                        contentPiece(id: $id) {
                            id
                            state
                        }
                    }
                """,
                "variables": {"id": content_id},
            },
            content_type="application/json",
        )
        assert state_resp.json()["data"]["contentPiece"]["state"] == "SUGGESTED_BY_AI"

        # Step 4: Approve the draft
        approve_resp = self.client.post(
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
                "variables": {"id": content_id, "action": "APPROVE", "feedback": "Great work!"},
            },
            content_type="application/json",
        )
        approve_data = approve_resp.json()
        assert "errors" not in approve_data, str(approve_data.get("errors"))
        assert approve_data["data"]["reviewContent"]["state"] == "APPROVED"

    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_full_workflow_with_translation(self, mock_openai: MagicMock) -> None:
        mock_instance = mock_openai.return_value
        mock_choice = mock_instance.chat.completions.create.return_value.choices[0]

        # First call: generateDraft, Second call: translateContent
        mock_choice.message.content = json.dumps(
            {"headline": "AI Draft Headline", "description": "AI draft description."}
        )

        campaign_id = _create_campaign(self.client)
        content_id = _create_content(self.client, campaign_id)

        self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        generateDraft(contentId: $id) { id state }
                    }
                """,
                "variables": {"id": content_id},
            },
            content_type="application/json",
        )

        # Translate — update mock response for translation
        mock_choice.message.content = json.dumps(
            {"headline": "Título traducido", "description": "Descripción traducida."}
        )

        translate_resp = self.client.post(
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
        translate_data = translate_resp.json()
        assert "errors" not in translate_data, str(translate_data.get("errors"))
        translated = translate_data["data"]["translateContent"]
        assert translated["headline"] == "Título traducido"
        assert translated["description"] == "Descripción traducida."
        assert translated["state"] == "SUGGESTED_BY_AI"
        assert translated["language"] == "es"
        assert translated["originalId"] == content_id
        assert translated["id"] != content_id

        # Verify translation via contentPiece query
        verify_resp = self.client.post(
            "/graphql",
            {
                "query": """
                    query($id: ID!) {
                        contentPiece(id: $id) {
                            id
                            state
                            language
                            originalId
                        }
                    }
                """,
                "variables": {"id": translated["id"]},
            },
            content_type="application/json",
        )
        verify_data = verify_resp.json()
        assert "errors" not in verify_data, str(verify_data.get("errors"))
        piece = verify_data["data"]["contentPiece"]
        assert piece["state"] == "SUGGESTED_BY_AI"
        assert piece["language"] == "es"
        assert piece["originalId"] == content_id

        # Verify state history exists for the translated piece
        history_resp = self.client.post(
            "/graphql",
            {
                "query": """
                    query($id: ID!) {
                        contentStateHistory(contentId: $id) {
                            fromState
                            toState
                            action
                        }
                    }
                """,
                "variables": {"id": translated["id"]},
            },
            content_type="application/json",
        )
        history_data = history_resp.json()
        assert "errors" not in history_data, str(history_data.get("errors"))
        history = history_data["data"]["contentStateHistory"]
        assert len(history) >= 1
        assert history[0]["fromState"] == "draft"
        assert history[0]["toState"] == "suggested_by_ai"
        assert history[0]["action"] == "GENERATE_AI"

    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_workflow_reject_then_edit_then_regenerate(self, mock_openai: MagicMock) -> None:
        mock_instance = mock_openai.return_value
        mock_choice = mock_instance.chat.completions.create.return_value.choices[0]

        mock_choice.message.content = json.dumps(
            {"headline": "First Draft", "description": "First attempt."}
        )

        campaign_id = _create_campaign(self.client)
        content_id = _create_content(self.client, campaign_id)

        # Generate AI draft
        self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        generateDraft(contentId: $id) { id state }
                    }
                """,
                "variables": {"id": content_id},
            },
            content_type="application/json",
        )

        # Reject
        reject_resp = self.client.post(
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
                "variables": {"id": content_id, "action": "REJECT", "feedback": "Not good enough"},
            },
            content_type="application/json",
        )
        assert reject_resp.json()["data"]["reviewContent"]["state"] == "REJECTED"

        # Edit (resets to DRAFT)
        edit_resp = self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!, $headline: String!) {
                        editContent(contentId: $id, headline: $headline) {
                            id
                            state
                            headline
                        }
                    }
                """,
                "variables": {"id": content_id, "headline": "Revised Headline"},
            },
            content_type="application/json",
        )
        edit_data = edit_resp.json()
        assert "errors" not in edit_data, str(edit_data.get("errors"))
        assert edit_data["data"]["editContent"]["state"] == "DRAFT"
        assert edit_data["data"]["editContent"]["headline"] == "Revised Headline"

        # Regenerate AI draft with new mock response
        mock_choice.message.content = json.dumps(
            {"headline": "Second Draft", "description": "Second attempt."}
        )

        regen_resp = self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        generateDraft(contentId: $id) { id headline state }
                    }
                """,
                "variables": {"id": content_id},
            },
            content_type="application/json",
        )
        regen_data = regen_resp.json()
        assert "errors" not in regen_data, str(regen_data.get("errors"))
        assert regen_data["data"]["generateDraft"]["state"] == "SUGGESTED_BY_AI"
        assert regen_data["data"]["generateDraft"]["headline"] == "Second Draft"

    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_websocket_broadcast_on_workflow_steps(self, mock_openai: MagicMock) -> None:
        mock_instance = mock_openai.return_value
        mock_choice = mock_instance.chat.completions.create.return_value.choices[0]
        mock_choice.message.content = json.dumps(
            {"headline": "WS Test", "description": "Testing WS broadcast."}
        )

        mock_channel_layer = MagicMock()
        mock_channel_layer.group_send = AsyncMock()

        with patch("apps.ws.signals.get_channel_layer", return_value=mock_channel_layer):
            campaign_id = _create_campaign(self.client)
            content_id = _create_content(self.client, campaign_id)

            # Generate draft triggers a broadcast (draft -> suggested_by_ai)
            self.client.post(
                "/graphql",
                {
                    "query": """
                        mutation($id: ID!) {
                            generateDraft(contentId: $id) { id state }
                        }
                    """,
                    "variables": {"id": content_id},
                },
                content_type="application/json",
            )

            assert mock_channel_layer.group_send.called
            args, _ = mock_channel_layer.group_send.call_args
            group_name, message = args
            assert group_name == f"content_{content_id}"
            assert message["type"] == "state.change"
            payload = message["payload"]
            assert payload["contentId"] == content_id
            assert payload["oldState"] == "draft"
            assert payload["newState"] == "suggested_by_ai"
            assert payload["action"] == "generate_ai"

            # Approve triggers another broadcast
            mock_channel_layer.group_send.reset_mock()

            self.client.post(
                "/graphql",
                {
                    "query": """
                        mutation($id: ID!, $action: ReviewAction!) {
                            reviewContent(contentId: $id, action: $action) {
                                id state
                            }
                        }
                    """,
                    "variables": {"id": content_id, "action": "APPROVE"},
                },
                content_type="application/json",
            )

            assert mock_channel_layer.group_send.called
            args, _ = mock_channel_layer.group_send.call_args
            payload = args[1]["payload"]
            assert payload["oldState"] == "suggested_by_ai"
            assert payload["newState"] == "approved"
            assert payload["action"] == "approve"

    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_workflow_content_pieces_list(self, mock_openai: MagicMock) -> None:
        mock_instance = mock_openai.return_value
        mock_choice = mock_instance.chat.completions.create.return_value.choices[0]
        mock_choice.message.content = json.dumps(
            {"headline": "List Test", "description": "Testing listing."}
        )

        campaign_id = _create_campaign(self.client)
        content_id = _create_content(self.client, campaign_id)

        # Create a second content piece
        resp2 = self.client.post(
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
                        "headline": "Second Piece",
                        "description": "Another piece for the campaign",
                    }
                },
            },
            content_type="application/json",
        )
        content_id2 = cast(str, resp2.json()["data"]["createContentPiece"]["id"])

        # Generate draft on first piece
        self.client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        generateDraft(contentId: $id) { id state }
                    }
                """,
                "variables": {"id": content_id},
            },
            content_type="application/json",
        )

        # Verify contentPieces returns both with correct states
        list_resp = self.client.post(
            "/graphql",
            {
                "query": """
                    query($cid: ID!) {
                        contentPieces(campaignId: $cid, page: 1, perPage: 10) {
                            totalCount
                            items {
                                id
                                state
                                headline
                            }
                        }
                    }
                """,
                "variables": {"cid": campaign_id},
            },
            content_type="application/json",
        )
        list_data = list_resp.json()
        assert "errors" not in list_data, str(list_data.get("errors"))
        pieces = list_data["data"]["contentPieces"]
        assert pieces["totalCount"] >= 2

        piece_map = {p["id"]: p for p in pieces["items"]}
        assert piece_map[content_id]["state"] == "SUGGESTED_BY_AI"
        assert piece_map[content_id]["headline"] == "List Test"
        assert piece_map[content_id2]["state"] == "DRAFT"
        assert piece_map[content_id2]["headline"] == "Second Piece"
