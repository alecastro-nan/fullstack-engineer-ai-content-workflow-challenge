from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from django.core.exceptions import ValidationError

from apps.campaigns.models import Campaign
from apps.campaigns.services import CampaignService
from apps.content.models import ContentPiece
from apps.content.services import ContentPieceService
from apps.reviews.enums import ReviewAction
from apps.reviews.models import StateHistory
from apps.reviews.services import ReviewService


@pytest.fixture
def campaign() -> Campaign:
    return CampaignService.create_campaign(name="WS Test Campaign")


@pytest.fixture
def content_piece(campaign: Campaign) -> ContentPiece:
    return ContentPieceService.create_content_piece(
        campaign_id=campaign.id,
        headline="WS Test",
        description="For WebSocket tests",
    )


@pytest.mark.django_db
class TestStateChangeBroadcast:
    def test_broadcast_called_on_state_history_creation(
        self, content_piece: ContentPiece
    ) -> None:
        mock_channel_layer = MagicMock()
        mock_channel_layer.group_send = AsyncMock()
        with patch("apps.ws.signals.get_channel_layer", return_value=mock_channel_layer):
            ReviewService.review_content(
                content_id=content_piece.id,
                action=ReviewAction.GENERATE_AI,
            )

            mock_channel_layer.group_send.assert_called_once()
            args, _ = mock_channel_layer.group_send.call_args
            group_name, message = args

            assert group_name == f"content_{content_piece.id}"
            assert message["type"] == "state.change"
            payload = message["payload"]
            assert payload["contentId"] == str(content_piece.id)
            assert payload["campaignId"] == str(content_piece.campaign_id)
            assert payload["oldState"] == "draft"
            assert payload["newState"] == "suggested_by_ai"
            assert payload["action"] == "generate_ai"
            assert "timestamp" in payload

    def test_broadcast_not_called_when_invalid_transition(
        self, content_piece: ContentPiece
    ) -> None:
        mock_channel_layer = MagicMock()
        mock_channel_layer.group_send = AsyncMock()
        with patch("apps.ws.signals.get_channel_layer", return_value=mock_channel_layer):
            with pytest.raises(ValidationError):
                ReviewService.review_content(
                    content_id=content_piece.id,
                    action=ReviewAction.APPROVE,
                )
            mock_channel_layer.group_send.assert_not_called()

    def test_event_payload_structure(self, content_piece: ContentPiece) -> None:
        mock_channel_layer = MagicMock()
        mock_channel_layer.group_send = AsyncMock()
        with patch("apps.ws.signals.get_channel_layer", return_value=mock_channel_layer):
            ReviewService.review_content(
                content_id=content_piece.id,
                action=ReviewAction.GENERATE_AI,
            )

            args, _ = mock_channel_layer.group_send.call_args
            payload = args[1]["payload"]

            assert isinstance(payload["contentId"], str)
            assert isinstance(payload["campaignId"], str)
            assert isinstance(payload["oldState"], str)
            assert isinstance(payload["newState"], str)
            assert isinstance(payload["action"], str)
            assert isinstance(payload["timestamp"], str)

    def test_no_channel_layer_does_not_crash(
        self, content_piece: ContentPiece
    ) -> None:
        with patch("apps.ws.signals.get_channel_layer", return_value=None):
            ReviewService.review_content(
                content_id=content_piece.id,
                action=ReviewAction.GENERATE_AI,
            )
