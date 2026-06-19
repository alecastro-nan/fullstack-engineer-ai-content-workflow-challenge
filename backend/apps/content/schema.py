import enum
import uuid

import strawberry
from django.core.exceptions import ValidationError
from graphql import GraphQLError

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
        campaign_id = str(piece.campaign.pk)
        original_id: strawberry.ID | None = None
        if piece.original is not None:
            original_id = strawberry.ID(str(piece.original.pk))
        return ContentPieceType(
            id=strawberry.ID(str(piece.id)),
            campaign_id=strawberry.ID(campaign_id),
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


@strawberry.type
class ContentPieceQueries:
    @strawberry.field
    def content_pieces(
        self,
        campaign_id: strawberry.ID | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> ContentPiecePage:
        if page < 1:
            page = 1
        if per_page < 1 or per_page > MAX_PER_PAGE:
            per_page = 20
        cid: uuid.UUID | None = None
        if campaign_id is not None:
            try:
                cid = uuid.UUID(str(campaign_id))
            except ValueError:
                return ContentPiecePage(items=[], total_count=0, page=page, per_page=per_page)
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
    def content_piece(self, id: strawberry.ID) -> ContentPieceType | None:
        try:
            piece_id = uuid.UUID(str(id))
        except ValueError:
            return None
        piece = ContentPieceService.get_content_piece_by_id(piece_id)
        if piece is None:
            return None
        return ContentPieceType.from_model(piece)


@strawberry.type
class ContentPieceMutations:
    @strawberry.mutation
    def create_content_piece(self, input: ContentPieceInput) -> ContentPieceType:
        try:
            campaign_id = uuid.UUID(str(input.campaign_id))
        except ValueError:
            raise GraphQLError("Invalid campaign ID") from None
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
        id: strawberry.ID,
        input: ContentPieceUpdateInput,
    ) -> ContentPieceType | None:
        try:
            piece_id = uuid.UUID(str(id))
        except ValueError:
            return None
        try:
            piece = ContentPieceService.update_content_piece(
                content_id=piece_id,
                headline=input.headline,
                description=input.description,
                body=input.body,
                language=input.language,
            )
        except ValidationError as e:
            raise GraphQLError(str(e)) from e
        if piece is None:
            return None
        return ContentPieceType.from_model(piece)

    @strawberry.mutation
    def delete_content_piece(self, id: strawberry.ID) -> bool:
        try:
            piece_id = uuid.UUID(str(id))
        except ValueError:
            return False
        return ContentPieceService.soft_delete_content_piece(piece_id)
