import uuid

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.campaigns.models import Campaign
from apps.campaigns.services import CampaignService
from apps.content.models import ContentPiece
from apps.content.services import ContentPieceService
from apps.reviews.models import StateHistory
from apps.reviews.services import ReviewAction, ReviewService


@pytest.fixture
def campaign() -> Campaign:
    return CampaignService.create_campaign(name="Review Test Campaign")


@pytest.fixture
def draft_content(campaign: Campaign) -> ContentPiece:
    return ContentPieceService.create_content_piece(
        campaign_id=campaign.id,
        headline="Test Piece",
        description="For review tests",
    )


@pytest.fixture
def ai_suggested_content(campaign: Campaign) -> ContentPiece:
    piece = ContentPieceService.create_content_piece(
        campaign_id=campaign.id,
        headline="AI Piece",
        description="AI suggested",
    )
    piece.state = ContentPiece.State.SUGGESTED_BY_AI
    piece.save(update_fields=["state"])
    return piece


@pytest.fixture
def reviewed_content(campaign: Campaign) -> ContentPiece:
    piece = ContentPieceService.create_content_piece(
        campaign_id=campaign.id,
        headline="Reviewed Piece",
        description="Already reviewed",
    )
    piece.state = ContentPiece.State.REVIEWED
    piece.save(update_fields=["state"])
    return piece


@pytest.fixture
def approved_content(campaign: Campaign) -> ContentPiece:
    piece = ContentPieceService.create_content_piece(
        campaign_id=campaign.id,
        headline="Approved Piece",
        description="Already approved",
    )
    piece.state = ContentPiece.State.APPROVED
    piece.save(update_fields=["state"])
    return piece


@pytest.fixture
def rejected_content(campaign: Campaign) -> ContentPiece:
    piece = ContentPieceService.create_content_piece(
        campaign_id=campaign.id,
        headline="Rejected Piece",
        description="Already rejected",
    )
    piece.state = ContentPiece.State.REJECTED
    piece.save(update_fields=["state"])
    return piece


@pytest.mark.django_db
class TestReviewService:
    def test_approve_from_suggested(self, ai_suggested_content: ContentPiece) -> None:
        piece = ReviewService.review_content(
            content_id=ai_suggested_content.id,
            action=ReviewAction.APPROVE,
        )
        assert piece is not None
        assert piece.state == ContentPiece.State.APPROVED

    def test_approve_from_reviewed(self, reviewed_content: ContentPiece) -> None:
        piece = ReviewService.review_content(
            content_id=reviewed_content.id,
            action=ReviewAction.APPROVE,
        )
        assert piece is not None
        assert piece.state == ContentPiece.State.APPROVED

    def test_reject_from_suggested(self, ai_suggested_content: ContentPiece) -> None:
        piece = ReviewService.review_content(
            content_id=ai_suggested_content.id,
            action=ReviewAction.REJECT,
        )
        assert piece is not None
        assert piece.state == ContentPiece.State.REJECTED

    def test_reject_from_reviewed(self, reviewed_content: ContentPiece) -> None:
        piece = ReviewService.review_content(
            content_id=reviewed_content.id,
            action=ReviewAction.REJECT,
        )
        assert piece is not None
        assert piece.state == ContentPiece.State.REJECTED

    def test_request_edits_from_suggested(self, ai_suggested_content: ContentPiece) -> None:
        piece = ReviewService.review_content(
            content_id=ai_suggested_content.id,
            action=ReviewAction.REQUEST_EDITS,
            feedback="Please revise the tone",
        )
        assert piece is not None
        assert piece.state == ContentPiece.State.REVIEWED

    def test_request_edits_from_reviewed(self, reviewed_content: ContentPiece) -> None:
        piece = ReviewService.review_content(
            content_id=reviewed_content.id,
            action=ReviewAction.REQUEST_EDITS,
            feedback="Still needs work",
        )
        assert piece is not None
        assert piece.state == ContentPiece.State.REVIEWED

    def test_reject_with_feedback(self, ai_suggested_content: ContentPiece) -> None:
        piece = ReviewService.review_content(
            content_id=ai_suggested_content.id,
            action=ReviewAction.REJECT,
            feedback="Does not match brand guidelines",
        )
        assert piece is not None
        assert piece.state == ContentPiece.State.REJECTED

    def test_edit_content_from_rejected(self, rejected_content: ContentPiece) -> None:
        piece = ReviewService.edit_content(
            content_id=rejected_content.id,
            headline="Edited Headline",
            description="Edited description",
        )
        assert piece is not None
        assert piece.headline == "Edited Headline"
        assert piece.description == "Edited description"
        assert piece.state == ContentPiece.State.DRAFT

    def test_edit_content_without_changing_state(self, draft_content: ContentPiece) -> None:
        piece = ReviewService.edit_content(
            content_id=draft_content.id,
            headline="New Headline",
        )
        assert piece is not None
        assert piece.headline == "New Headline"
        assert piece.state == ContentPiece.State.DRAFT

    def test_approve_from_draft_raises_error(self, draft_content: ContentPiece) -> None:
        msg = "Cannot transition from 'draft' with action 'approve'"
        with pytest.raises(ValidationError, match=msg):
            ReviewService.review_content(
                content_id=draft_content.id,
                action=ReviewAction.APPROVE,
            )

    def test_approve_from_approved_raises_error(self, approved_content: ContentPiece) -> None:
        with pytest.raises(ValidationError):
            ReviewService.review_content(
                content_id=approved_content.id,
                action=ReviewAction.APPROVE,
            )

    def test_reject_from_draft_raises_error(self, draft_content: ContentPiece) -> None:
        with pytest.raises(ValidationError):
            ReviewService.review_content(
                content_id=draft_content.id,
                action=ReviewAction.REJECT,
            )

    def test_reject_from_rejected_raises_error(self, rejected_content: ContentPiece) -> None:
        with pytest.raises(ValidationError):
            ReviewService.review_content(
                content_id=rejected_content.id,
                action=ReviewAction.REJECT,
            )

    def test_request_edits_from_draft_raises_error(self, draft_content: ContentPiece) -> None:
        with pytest.raises(ValidationError):
            ReviewService.review_content(
                content_id=draft_content.id,
                action=ReviewAction.REQUEST_EDITS,
            )

    def test_request_edits_from_approved_raises_error(self, approved_content: ContentPiece) -> None:
        with pytest.raises(ValidationError):
            ReviewService.review_content(
                content_id=approved_content.id,
                action=ReviewAction.REQUEST_EDITS,
            )

    def test_review_nonexistent_content_returns_none(self) -> None:
        result = ReviewService.review_content(
            content_id=uuid.uuid4(),
            action=ReviewAction.APPROVE,
        )
        assert result is None

    def test_edit_nonexistent_content_returns_none(self) -> None:
        result = ReviewService.edit_content(
            content_id=uuid.uuid4(),
            headline="Nope",
        )
        assert result is None

    def test_review_with_empty_feedback(self, ai_suggested_content: ContentPiece) -> None:
        piece = ReviewService.review_content(
            content_id=ai_suggested_content.id,
            action=ReviewAction.REJECT,
            feedback="",
        )
        assert piece is not None
        assert piece.state == ContentPiece.State.REJECTED

    def test_review_with_whitespace_feedback(self, ai_suggested_content: ContentPiece) -> None:
        piece = ReviewService.review_content(
            content_id=ai_suggested_content.id,
            action=ReviewAction.REQUEST_EDITS,
            feedback="   ",
        )
        assert piece is not None
        assert piece.state == ContentPiece.State.REVIEWED


@pytest.mark.django_db
class TestStateHistory:
    def test_state_history_created_on_review(self, ai_suggested_content: ContentPiece) -> None:
        ReviewService.review_content(
            content_id=ai_suggested_content.id,
            action=ReviewAction.APPROVE,
        )
        history = StateHistory.objects.filter(content_piece=ai_suggested_content)
        assert history.count() == 1
        record = history.first()
        assert record is not None
        assert record.from_state == ContentPiece.State.SUGGESTED_BY_AI
        assert record.to_state == ContentPiece.State.APPROVED
        assert record.action == ReviewAction.APPROVE.value

    def test_state_history_includes_feedback(self, ai_suggested_content: ContentPiece) -> None:
        ReviewService.review_content(
            content_id=ai_suggested_content.id,
            action=ReviewAction.REJECT,
            feedback="Bad tone",
        )
        record = StateHistory.objects.get(content_piece=ai_suggested_content)
        assert record.feedback == "Bad tone"

    def test_state_history_created_on_edit(self, rejected_content: ContentPiece) -> None:
        ReviewService.edit_content(
            content_id=rejected_content.id,
            headline="Fixed",
        )
        history = StateHistory.objects.filter(content_piece=rejected_content)
        assert history.count() == 1
        record = history.first()
        assert record is not None
        assert record.from_state == ContentPiece.State.REJECTED
        assert record.to_state == ContentPiece.State.DRAFT
        assert record.action == ReviewAction.EDIT.value

    def test_multiple_transitions_all_recorded(
        self, ai_suggested_content: ContentPiece
    ) -> None:
        ReviewService.review_content(
            content_id=ai_suggested_content.id,
            action=ReviewAction.REJECT,
        )
        ReviewService.edit_content(
            content_id=ai_suggested_content.id,
            headline="Retry",
        )
        history = StateHistory.objects.filter(
            content_piece=ai_suggested_content
        ).order_by("created_at")
        assert history.count() == 2
        assert history[0].from_state == ContentPiece.State.SUGGESTED_BY_AI
        assert history[0].to_state == ContentPiece.State.REJECTED
        assert history[1].from_state == ContentPiece.State.REJECTED
        assert history[1].to_state == ContentPiece.State.DRAFT

    def test_state_history_has_timestamps(
        self, ai_suggested_content: ContentPiece
    ) -> None:
        before = timezone.now()
        ReviewService.review_content(
            content_id=ai_suggested_content.id,
            action=ReviewAction.APPROVE,
        )
        after = timezone.now()
        record = StateHistory.objects.get(content_piece=ai_suggested_content)
        assert record.created_at is not None
        assert before <= record.created_at <= after

    def test_invalid_transition_does_not_create_history(
        self, draft_content: ContentPiece
    ) -> None:
        with pytest.raises(ValidationError):
            ReviewService.review_content(
                content_id=draft_content.id,
                action=ReviewAction.APPROVE,
            )
        assert StateHistory.objects.count() == 0
