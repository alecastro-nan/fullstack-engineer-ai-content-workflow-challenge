import enum
import uuid

import strawberry
from django.core.exceptions import ValidationError
from graphql import GraphQLError

from apps.auth.utils import get_user_or_error
from apps.campaigns.services import CampaignService
from apps.content.models import ContentPiece
from apps.content.services import ContentPieceService

MAX_PER_PAGE = 100


@strawberry.enum
class ContentState(enum.Enum):
    DRAFT = "draft"
    SUGGESTED_BY_AI = "suggested_by_ai"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


@strawberry.input
class ContentPieceInput:
    campaign_id: strawberry.ID
    headline: str
    description: str = ""
    body: str = ""
    language: str = "en"


@strawberry.input
class ContentPieceUpdateInput:
    headline: str | None = None
    description: str | None = None
    body: str | None = None
    language: str | None = None


@strawberry.type
class ContentPieceType:
    id: strawberry.ID
    campaign_id: strawberry.ID
    headline: str
    description: str
    body: str
    language: str
    state: ContentState
    original_id: strawberry.ID | None
    created_at: str
    updated_at: str

    @staticmethod
    def from_model(piece: ContentPiece) -> "ContentPieceType":
        original_id: strawberry.ID | None = None
        if piece.original_id is not None:  # type: ignore[attr-defined]
            original_id = strawberry.ID(str(piece.original_id))  # type: ignore[attr-defined]
        return ContentPieceType(
            id=strawberry.ID(str(piece.id)),
            campaign_id=strawberry.ID(str(piece.campaign_id)),  # type: ignore[attr-defined]
            headline=piece.headline,
            description=piece.description,
            body=piece.body,
            language=piece.language,
            state=ContentState(piece.state),
            original_id=original_id,
            created_at=piece.created_at.isoformat(),
            updated_at=piece.updated_at.isoformat(),
        )


@strawberry.type
class ContentPiecePage:
    items: list[ContentPieceType]
    total_count: int
    page: int
    per_page: int


def _verify_campaign_owner(campaign_id: uuid.UUID, user: object) -> None:
    campaign = CampaignService.get_campaign_by_id(campaign_id)
    if campaign is None or campaign.owner != user:
        raise GraphQLError("Campaign not found")


@strawberry.type
class ContentPieceQueries:
    @strawberry.field
    def content_pieces(
        self,
        info: strawberry.types.info.Info,
        campaign_id: strawberry.ID | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> ContentPiecePage:
        user = get_user_or_error(info)
        if page < 1:
            raise GraphQLError("Page must be >= 1")
        if per_page < 1 or per_page > MAX_PER_PAGE:
            raise GraphQLError(f"Per page must be between 1 and {MAX_PER_PAGE}")
        cid: uuid.UUID | None = None
        if campaign_id is not None:
            try:
                cid = uuid.UUID(str(campaign_id))
            except ValueError:
                raise GraphQLError("Invalid campaign ID") from None
            _verify_campaign_owner(cid, user)
        qs = ContentPieceService.list_content_pieces(campaign_id=cid)
        total = qs.count()
        offset = (page - 1) * per_page
        items = qs[offset : offset + per_page]
        return ContentPiecePage(
            items=[ContentPieceType.from_model(c) for c in items],
            total_count=total,
            page=page,
            per_page=per_page,
        )

    @strawberry.field
    def content_piece(
        self, info: strawberry.types.info.Info, id: strawberry.ID
    ) -> ContentPieceType | None:
        user = get_user_or_error(info)
        try:
            piece_id = uuid.UUID(str(id))
        except ValueError:
            raise GraphQLError("Invalid content piece ID") from None
        piece = ContentPieceService.get_content_piece_by_id(piece_id)
        if piece is None:
            return None
        if piece.campaign.owner != user:
            return None
        return ContentPieceType.from_model(piece)


@strawberry.type
class ContentPieceMutations:
    @strawberry.mutation
    def create_content_piece(
        self, info: strawberry.types.info.Info, input: ContentPieceInput
    ) -> ContentPieceType:
        user = get_user_or_error(info)
        try:
            campaign_id = uuid.UUID(str(input.campaign_id))
        except ValueError:
            raise GraphQLError("Invalid campaign ID") from None
        _verify_campaign_owner(campaign_id, user)
        try:
            piece = ContentPieceService.create_content_piece(
                campaign_id=campaign_id,
                headline=input.headline,
                description=input.description,
                body=input.body,
                language=input.language,
            )
        except ValidationError as e:
            raise GraphQLError(str(e)) from e
        return ContentPieceType.from_model(piece)

    @strawberry.mutation
    def update_content_piece(
        self,
        info: strawberry.types.info.Info,
        id: strawberry.ID,
        input: ContentPieceUpdateInput,
    ) -> ContentPieceType | None:
        user = get_user_or_error(info)
        try:
            piece_id = uuid.UUID(str(id))
        except ValueError:
            raise GraphQLError("Invalid content piece ID") from None
        piece = ContentPieceService.get_content_piece_by_id(piece_id)
        if piece is None:
            return None
        if piece.campaign.owner != user:
            return None
        try:
            updated = ContentPieceService.update_content_piece(
                content_id=piece_id,
                headline=input.headline,
                description=input.description,
                body=input.body,
                language=input.language,
            )
        except ValidationError as e:
            raise GraphQLError(str(e)) from e
        if updated is None:
            return None
        return ContentPieceType.from_model(updated)

    @strawberry.mutation
    def delete_content_piece(self, info: strawberry.types.info.Info, id: strawberry.ID) -> bool:
        user = get_user_or_error(info)
        try:
            piece_id = uuid.UUID(str(id))
        except ValueError:
            raise GraphQLError("Invalid content piece ID") from None
        piece = ContentPieceService.get_content_piece_by_id(piece_id)
        if piece is None or piece.campaign.owner != user:
            return False
        return ContentPieceService.soft_delete_content_piece(piece_id)
