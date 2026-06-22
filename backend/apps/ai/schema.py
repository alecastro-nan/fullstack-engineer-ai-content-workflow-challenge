import logging
import uuid

import strawberry
from graphql import GraphQLError

from apps.ai.exceptions import AIProviderError
from apps.ai.services import AiService
from apps.content.models import ContentPiece
from apps.content.schema import ContentPieceType
from apps.content.services import ContentPieceService
from apps.reviews.enums import ReviewAction
from apps.reviews.models import StateHistory

logger = logging.getLogger(__name__)


@strawberry.type
class AiQuery:
    pass


@strawberry.type
class AiMutation:
    @strawberry.mutation
    def generate_draft(self, content_id: strawberry.ID) -> ContentPieceType | None:
        try:
            piece_id = uuid.UUID(str(content_id))
        except ValueError:
            raise GraphQLError("Invalid content piece ID") from None

        piece = ContentPieceService.get_content_piece_by_id(piece_id)
        if piece is None:
            return None

        if piece.state != ContentPiece.State.DRAFT:
            raise GraphQLError(
                f"Cannot generate draft for content in state '{piece.state}'. "
                "Content must be in 'draft' state."
            )

        brief = piece.description or piece.headline
        if not brief:
            raise GraphQLError("Content piece has no description or headline to use as brief")

        try:
            draft = AiService.generate_draft(brief)
        except AIProviderError as e:
            logger.error("AI draft generation failed", exc_info=True)
            raise GraphQLError("AI draft generation failed. Please try again later.") from e

        from_state = piece.state
        piece.headline = draft.headline
        piece.description = draft.description
        piece.state = ContentPiece.State.SUGGESTED_BY_AI
        piece.save(update_fields=["headline", "description", "state", "updated_at"])

        StateHistory.objects.create(
            content_piece=piece,
            from_state=from_state,
            to_state=piece.state,
            action=ReviewAction.GENERATE_AI.value,
        )

        return ContentPieceType.from_model(piece)
