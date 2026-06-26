import logging
import uuid

import strawberry
from graphql import GraphQLError

from apps.ai.exceptions import AIProviderError
from apps.ai.services import AiService
from apps.auth.utils import get_user_or_error
from apps.content.models import ContentPiece
from apps.content.schema import ContentPieceType
from apps.content.services import ContentPieceService
from apps.reviews.enums import ReviewAction
from apps.reviews.models import StateHistory

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES: set[str] = {"es", "fr", "de", "pt", "it", "ja", "zh"}


@strawberry.type
class AiQuery:
    pass


@strawberry.type
class AiMutation:
    @strawberry.mutation
    def generate_draft(
        self, info: strawberry.types.info.Info, content_id: strawberry.ID
    ) -> ContentPieceType | None:
        user = get_user_or_error(info)
        try:
            piece_id = uuid.UUID(str(content_id))
        except ValueError:
            raise GraphQLError("Invalid content piece ID") from None

        piece = ContentPieceService.get_content_piece_by_id(piece_id)
        if piece is None:
            return None

        if piece.campaign.owner != user:
            return None

        if piece.state != ContentPiece.State.DRAFT:
            raise GraphQLError(
                f"Cannot generate draft for content in state '{piece.state}'. "
                "Content must be in 'draft' state."
            )

        brief = piece.description or piece.headline
        if not brief:
            raise GraphQLError("Content piece has no description or headline to use as brief")
        if len(brief) > 5000:
            raise GraphQLError("Brief must be 5000 characters or fewer")

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

    @strawberry.mutation
    def translate_content(
        self,
        info: strawberry.types.info.Info,
        content_id: strawberry.ID,
        target_language: str,
    ) -> ContentPieceType | None:
        user = get_user_or_error(info)
        try:
            piece_id = uuid.UUID(str(content_id))
        except ValueError:
            raise GraphQLError("Invalid content piece ID") from None

        piece = ContentPieceService.get_content_piece_by_id(piece_id)
        if piece is None:
            return None

        if piece.campaign.owner != user:
            return None

        if target_language not in SUPPORTED_LANGUAGES:
            raise GraphQLError(
                f"Unsupported language: '{target_language}'. "
                f"Supported languages: {', '.join(sorted(SUPPORTED_LANGUAGES))}"
            )

        text = f"Headline: {piece.headline}\nDescription: {piece.description}"

        try:
            translation = AiService.translate(text, target_language)
        except Exception as e:
            logger.error("AI translation failed", exc_info=True)
            raise GraphQLError("AI translation failed. Please try again later.") from e

        translated_piece = ContentPiece.objects.create(
            campaign=piece.campaign,
            headline=translation.headline,
            description=translation.description,
            body=piece.body,
            language=target_language,
            state=ContentPiece.State.SUGGESTED_BY_AI,
            original=piece,
        )

        StateHistory.objects.create(
            content_piece=translated_piece,
            from_state=ContentPiece.State.DRAFT,
            to_state=ContentPiece.State.SUGGESTED_BY_AI,
            action=ReviewAction.GENERATE_AI.value,
        )

        return ContentPieceType.from_model(translated_piece)
