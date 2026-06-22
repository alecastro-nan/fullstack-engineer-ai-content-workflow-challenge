import logging
import uuid

import strawberry
from graphql import GraphQLError

from apps.ai.services import AiService
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
    def translate_content(
        self,
        content_id: strawberry.ID,
        target_language: str,
    ) -> ContentPieceType | None:
        try:
            piece_id = uuid.UUID(str(content_id))
        except ValueError:
            raise GraphQLError("Invalid content piece ID") from None

        piece = ContentPieceService.get_content_piece_by_id(piece_id)
        if piece is None:
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
