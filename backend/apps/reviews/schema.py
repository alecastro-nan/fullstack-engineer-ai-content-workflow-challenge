import enum
import uuid

import strawberry
from django.core.exceptions import ValidationError
from graphql import GraphQLError

from apps.content.schema import ContentPieceType
from apps.reviews.services import ReviewAction as ReviewActionService
from apps.reviews.services import ReviewService


@strawberry.enum
class ReviewAction(enum.Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_EDITS = "request_edits"


@strawberry.type
class StateHistoryType:
    id: strawberry.ID
    content_piece_id: strawberry.ID
    from_state: str
    to_state: str
    action: str
    feedback: str
    created_at: str


@strawberry.type
class ReviewQuery:
    @strawberry.field
    def content_state_history(
        self,
        content_id: strawberry.ID,
    ) -> list[StateHistoryType]:
        try:
            piece_id = uuid.UUID(str(content_id))
        except ValueError:
            raise GraphQLError("Invalid content piece ID") from None
        from apps.reviews.models import StateHistory
        records = StateHistory.objects.filter(content_piece_id=piece_id).order_by("created_at")
        return [
            StateHistoryType(
                id=strawberry.ID(str(r.id)),
                content_piece_id=strawberry.ID(str(r.content_piece_id)),  # type: ignore[attr-defined]
                from_state=r.from_state,
                to_state=r.to_state,
                action=r.action,
                feedback=r.feedback,
                created_at=r.created_at.isoformat(),
            )
            for r in records
        ]


@strawberry.input
class ReviewContentInput:
    content_id: strawberry.ID
    action: ReviewAction
    feedback: str = ""


@strawberry.type
class ReviewMutation:
    @strawberry.mutation
    def review_content(
        self,
        content_id: strawberry.ID,
        action: ReviewAction,
        feedback: str = "",
    ) -> ContentPieceType | None:
        try:
            piece_id = uuid.UUID(str(content_id))
        except ValueError:
            raise GraphQLError("Invalid content piece ID") from None
        try:
            piece = ReviewService.review_content(
                content_id=piece_id,
                action=ReviewActionService(action.value),
                feedback=feedback,
            )
        except ValidationError as e:
            raise GraphQLError(str(e)) from e
        if piece is None:
            return None
        return ContentPieceType.from_model(piece)

    @strawberry.mutation
    def edit_content(
        self,
        content_id: strawberry.ID,
        headline: str | None = None,
        description: str | None = None,
        body: str | None = None,
    ) -> ContentPieceType | None:
        try:
            piece_id = uuid.UUID(str(content_id))
        except ValueError:
            raise GraphQLError("Invalid content piece ID") from None
        try:
            piece = ReviewService.edit_content(
                content_id=piece_id,
                headline=headline,
                description=description,
                body=body,
            )
        except ValidationError as e:
            raise GraphQLError(str(e)) from e
        if piece is None:
            return None
        return ContentPieceType.from_model(piece)
