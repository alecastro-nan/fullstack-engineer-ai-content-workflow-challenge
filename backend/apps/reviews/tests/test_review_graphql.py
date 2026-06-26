import json
from typing import Any
from unittest.mock import patch

import pytest
from django.test import Client
from django.test.utils import override_settings

from apps.auth.test_utils import make_auth_client


@pytest.mark.django_db
class TestReviewMutations:
    def _create_campaign_and_content(self, client: Any) -> tuple[str, str]:
        camp_resp = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        createCampaign(input: { name: "Review Test" }) {
                            id
                        }
                    }
                """
            },
            content_type="application/json",
        )
        campaign_id = camp_resp.json()["data"]["createCampaign"]["id"]

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
                        "headline": "Review Content",
                        "description": "Review Description",
                    }
                },
            },
            content_type="application/json",
        )
        content_id = content_resp.json()["data"]["createContentPiece"]["id"]
        return campaign_id, content_id

    def _generate_draft(self, client: Any, content_id: str) -> None:
        client.post(
            "/graphql",
            {
                "query": """
                    mutation($contentId: ID!) {
                        generateDraft(contentId: $contentId) { id }
                    }
                """,
                "variables": {"contentId": content_id},
            },
            content_type="application/json",
        )

    def test_approve_content(self) -> None:
        # Test-only dummy key — not a real credential
        with override_settings(OPENAI_API_KEY="test-invalid-key"), \
             patch("apps.ai.providers.openai_provider.OpenAI") as mock_openai:
            mock_client = mock_openai.return_value
            mock_choice = mock_client.chat.completions.create.return_value.choices[0]
            mock_choice.message.content = json.dumps(
                {"headline": "AI draft", "description": "AI generated text"}
            )
            client = make_auth_client()
            _, content_id = self._create_campaign_and_content(client)
            self._generate_draft(client, content_id)

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
            assert response.status_code == 200
            assert response.json()["data"]["reviewContent"]["state"] == "APPROVED"

    def test_reject_content(self) -> None:
        # Test-only dummy key — not a real credential
        with override_settings(OPENAI_API_KEY="test-invalid-key"), \
             patch("apps.ai.providers.openai_provider.OpenAI") as mock_openai:
            mock_client = mock_openai.return_value
            mock_choice = mock_client.chat.completions.create.return_value.choices[0]
            mock_choice.message.content = json.dumps(
                {"headline": "AI draft", "description": "AI generated text"}
            )
            client = make_auth_client()
            _, content_id = self._create_campaign_and_content(client)
            self._generate_draft(client, content_id)

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
                    "variables": {"id": content_id, "action": "REJECT", "feedback": "Needs work"},
                },
                content_type="application/json",
            )
            assert response.status_code == 200
            assert response.json()["data"]["reviewContent"]["state"] == "REJECTED"

    def test_invalid_action(self) -> None:
        # Test-only dummy key — not a real credential
        with override_settings(OPENAI_API_KEY="test-invalid-key"), \
             patch("apps.ai.providers.openai_provider.OpenAI") as mock_openai:
            mock_client = mock_openai.return_value
            mock_choice = mock_client.chat.completions.create.return_value.choices[0]
            mock_choice.message.content = json.dumps(
                {"headline": "AI draft", "description": "AI generated text"}
            )
            client = make_auth_client()
            _, content_id = self._create_campaign_and_content(client)
            self._generate_draft(client, content_id)

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
                    "variables": {"id": content_id, "action": "INVALID"},
                },
                content_type="application/json",
            )
            assert response.status_code == 200
            assert response.json().get("errors") is not None

    def test_review_content_not_found(self) -> None:
        client = make_auth_client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($action: ReviewAction!) {
                        reviewContent(
                            contentId: "00000000-0000-0000-0000-000000000000",
                            action: $action
                        ) {
                            id
                        }
                    }
                """,
                "variables": {"action": "APPROVE"},
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["data"]["reviewContent"] is None

    def test_edit_content(self) -> None:
        client = make_auth_client()
        _, content_id = self._create_campaign_and_content(client)

        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        editContent(
                            contentId: $id,
                            headline: "Edited Headline",
                            description: "Edited Description",
                        ) {
                            id
                            headline
                            description
                        }
                    }
                """,
                "variables": {"id": content_id},
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()["data"]["editContent"]
        assert data["headline"] == "Edited Headline"

    def test_content_state_history(self) -> None:
        client = make_auth_client()
        _, content_id = self._create_campaign_and_content(client)

        history_resp = client.post(
            "/graphql",
            {
                "query": """
                    query($contentId: ID!) {
                        contentStateHistory(contentId: $contentId) {
                            id
                            fromState
                            toState
                            action
                        }
                    }
                """,
                "variables": {"contentId": content_id},
            },
            content_type="application/json",
        )
        assert history_resp.status_code == 200
        history = history_resp.json()["data"]["contentStateHistory"]
        assert history == []

    def test_content_state_history_bad_uuid(self) -> None:
        client = make_auth_client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    query {
                        contentStateHistory(contentId: "not-a-uuid") {
                            id
                        }
                    }
                """
            },
            content_type="application/json",
        )
        assert response.json().get("errors") is not None

    def test_content_state_history_not_found(self) -> None:
        client = make_auth_client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    query {
                        contentStateHistory(
                            contentId: "00000000-0000-0000-0000-000000000000"
                        ) {
                            id
                        }
                    }
                """
            },
            content_type="application/json",
        )
        assert response.json()["data"]["contentStateHistory"] == []

    def test_review_content_bad_uuid(self) -> None:
        client = make_auth_client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        reviewContent(contentId: "not-a-uuid", action: APPROVE) {
                            id
                        }
                    }
                """
            },
            content_type="application/json",
        )
        assert response.json().get("errors") is not None

    def test_review_content_invalid_transition(self) -> None:
        client = make_auth_client()
        _, content_id = self._create_campaign_and_content(client)
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
        assert response.json().get("errors") is not None

    def test_edit_content_bad_uuid(self) -> None:
        client = make_auth_client()
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation {
                        editContent(contentId: "not-a-uuid", headline: "Test") {
                            id
                        }
                    }
                """
            },
            content_type="application/json",
        )
        assert response.json().get("errors") is not None

    def test_edit_content_not_owned(self) -> None:
        from django.contrib.auth.models import User

        from apps.auth.services import create_access_token

        client_a = make_auth_client()
        _, content_id = self._create_campaign_and_content(client_a)

        other_user = User.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password="testpass123",
        )
        other_token = create_access_token(other_user)
        client_b = Client()
        client_b.defaults["HTTP_AUTHORIZATION"] = f"Bearer {other_token}"

        response = client_b.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        editContent(contentId: $id, headline: "Hacked") {
                            id
                        }
                    }
                """,
                "variables": {"id": content_id},
            },
            content_type="application/json",
        )
        assert response.json()["data"]["editContent"] is None

    def test_edit_content_no_fields_triggers_validation(self) -> None:
        client = make_auth_client()
        _, content_id = self._create_campaign_and_content(client)
        response = client.post(
            "/graphql",
            {
                "query": """
                    mutation($id: ID!) {
                        editContent(contentId: $id) { id }
                    }
                """,
                "variables": {"id": content_id},
            },
            content_type="application/json",
        )
        assert response.json().get("errors") is not None
