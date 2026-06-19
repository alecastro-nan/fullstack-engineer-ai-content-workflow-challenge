import uuid

from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from apps.campaigns.models import Campaign
from apps.content.models import ContentPiece

MAX_HEADLINE_LENGTH = 255
MAX_LANGUAGE_LENGTH = 10


class ContentPieceService:
    @staticmethod
    def _validate_headline(headline: str) -> str:
        stripped = headline.strip()
        if not stripped:
            raise ValidationError("Headline cannot be empty", code="invalid")
        if len(stripped) > MAX_HEADLINE_LENGTH:
            raise ValidationError(
                f"Headline too long (max {MAX_HEADLINE_LENGTH} characters)",
                code="invalid",
            )
        return stripped

    @staticmethod
    def _validate_language(language: str) -> str:
        stripped = language.strip()
        if not stripped:
            raise ValidationError("Language cannot be empty", code="invalid")
        if len(stripped) > MAX_LANGUAGE_LENGTH:
            raise ValidationError(
                f"Language code too long (max {MAX_LANGUAGE_LENGTH} characters)",
                code="invalid",
            )
        return stripped

    @staticmethod
    def _validate_campaign(campaign_id: uuid.UUID) -> Campaign:
        try:
            campaign = Campaign.objects.get(id=campaign_id, is_deleted=False)
        except Campaign.DoesNotExist:
            raise ValidationError(
                f"Campaign with id '{campaign_id}' does not exist",
                code="invalid",
            ) from None
        return campaign

    @staticmethod
    def create_content_piece(
        campaign_id: uuid.UUID,
        headline: str,
        description: str = "",
        body: str = "",
        language: str = "en",
    ) -> ContentPiece:
        validated_headline = ContentPieceService._validate_headline(headline)
        validated_language = ContentPieceService._validate_language(language)
        campaign = ContentPieceService._validate_campaign(campaign_id)
        return ContentPiece.objects.create(
            campaign=campaign,
            headline=validated_headline,
            description=description.strip(),
            body=body.strip(),
            language=validated_language,
        )

    @staticmethod
    def get_content_piece_by_id(content_id: uuid.UUID) -> ContentPiece | None:
        try:
            return ContentPiece.objects.get(id=content_id, is_deleted=False)
        except ContentPiece.DoesNotExist:
            return None

    @staticmethod
    def list_content_pieces(
        campaign_id: uuid.UUID | None = None,
    ) -> QuerySet[ContentPiece]:
        qs = ContentPiece.objects.filter(is_deleted=False)
        if campaign_id is not None:
            qs = qs.filter(campaign_id=campaign_id)
        return qs.order_by("-created_at")

    @staticmethod
    def update_content_piece(
        content_id: uuid.UUID,
        headline: str | None = None,
        description: str | None = None,
        body: str | None = None,
        language: str | None = None,
    ) -> ContentPiece | None:
        piece = ContentPieceService.get_content_piece_by_id(content_id)
        if piece is None:
            return None
        if headline is not None:
            piece.headline = ContentPieceService._validate_headline(headline)
        if description is not None:
            piece.description = description.strip()
        if body is not None:
            piece.body = body.strip()
        if language is not None:
            piece.language = ContentPieceService._validate_language(language)
        piece.save()
        return piece

    @staticmethod
    def soft_delete_content_piece(content_id: uuid.UUID) -> bool:
        piece = ContentPieceService.get_content_piece_by_id(content_id)
        if piece is None:
            return False
        piece.is_deleted = True
        piece.save(update_fields=["is_deleted", "updated_at"])
        return True
