import uuid

from django.core.exceptions import ValidationError

from apps.content.models import ContentPiece
from apps.content.services import ContentPieceService
from apps.reviews.enums import ReviewAction
from apps.reviews.models import StateHistory

TERMINAL_STATES = {
    ContentPiece.State.APPROVED,
}

MAX_FEEDBACK_LENGTH = 2000

VALID_TRANSITIONS: dict[str, dict[str, str]] = {
    ContentPiece.State.DRAFT: {},
    ContentPiece.State.SUGGESTED_BY_AI: {
        ReviewAction.APPROVE.value: ContentPiece.State.APPROVED,
        ReviewAction.REJECT.value: ContentPiece.State.REJECTED,
        ReviewAction.REQUEST_EDITS.value: ContentPiece.State.REVIEWED,
    },
    ContentPiece.State.REVIEWED: {
        ReviewAction.APPROVE.value: ContentPiece.State.APPROVED,
        ReviewAction.REJECT.value: ContentPiece.State.REJECTED,
        ReviewAction.REQUEST_EDITS.value: ContentPiece.State.REVIEWED,
    },
    ContentPiece.State.APPROVED: {},
    ContentPiece.State.REJECTED: {},
}


class ReviewService:
    @staticmethod
    def _validate_transition(
        from_state: str,
        action: str,
    ) -> str:
        allowed = VALID_TRANSITIONS.get(from_state, {})
        to_state = allowed.get(action)
        if to_state is None:
            raise ValidationError(
                f"Cannot transition from '{from_state}' with action '{action}'",
                code="invalid_transition",
            )
        return to_state

    @staticmethod
    def _record_history(
        content_piece: ContentPiece,
        from_state: str,
        to_state: str,
        action: str,
        feedback: str = "",
    ) -> None:
        StateHistory.objects.create(
            content_piece=content_piece,
            from_state=from_state,
            to_state=to_state,
            action=action,
            feedback=feedback.strip(),
        )

    @staticmethod
    def review_content(
        content_id: uuid.UUID,
        action: ReviewAction,
        feedback: str = "",
    ) -> ContentPiece | None:
        piece = ContentPieceService.get_content_piece_by_id(content_id)
        if piece is None:
            return None

        if len(feedback) > MAX_FEEDBACK_LENGTH:
            raise ValidationError(
                f"Feedback too long (max {MAX_FEEDBACK_LENGTH} characters)",
                code="invalid",
            )

        action_value = action.value
        from_state = piece.state
        to_state = ReviewService._validate_transition(from_state, action_value)

        piece.state = to_state
        piece.save(update_fields=["state", "updated_at"])

        ReviewService._record_history(piece, from_state, to_state, action_value, feedback)
        return piece

    @staticmethod
    def edit_content(
        content_id: uuid.UUID,
        headline: str | None = None,
        description: str | None = None,
        body: str | None = None,
    ) -> ContentPiece | None:
        if headline is None and description is None and body is None:
            raise ValidationError(
                "At least one field must be provided to edit content",
                code="no_changes",
            )

        piece = ContentPieceService.get_content_piece_by_id(content_id)
        if piece is None:
            return None

        if piece.state in TERMINAL_STATES:
            raise ValidationError(
                f"Cannot edit content in terminal state '{piece.state}'",
                code="terminal_state",
            )

        from_state = piece.state
        update_fields: list[str] = []
        changed = False

        if headline is not None:
            validated = ContentPieceService._validate_headline(headline)
            if validated != piece.headline:
                piece.headline = validated
                update_fields.append("headline")
                changed = True
        if description is not None:
            validated = ContentPieceService._validate_description(description)
            if validated != piece.description:
                piece.description = validated
                update_fields.append("description")
                changed = True
        if body is not None:
            validated = ContentPieceService._validate_body(body)
            if validated != piece.body:
                piece.body = validated
                update_fields.append("body")
                changed = True

        if changed:
            if from_state != ContentPiece.State.DRAFT:
                piece.state = ContentPiece.State.DRAFT
                update_fields.append("state")
            update_fields.append("updated_at")
            piece.save(update_fields=update_fields)
            if from_state != ContentPiece.State.DRAFT:
                ReviewService._record_history(
                    piece,
                    from_state,
                    ContentPiece.State.DRAFT,
                    ReviewAction.EDIT.value,
                )

        return piece
