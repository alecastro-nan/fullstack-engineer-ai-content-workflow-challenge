import enum
import uuid

import strawberry
from django.core.exceptions import ValidationError
from graphql import GraphQLError

from apps.campaigns.models import Campaign
from apps.campaigns.services import CampaignService

MAX_PER_PAGE = 100


@strawberry.enum
class CampaignStatus(enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


@strawberry.input
class CampaignInput:
    name: str
    description: str = ""


@strawberry.input
class CampaignUpdateInput:
    name: str | None = None
    description: str | None = None
    status: CampaignStatus | None = None


@strawberry.type
class CampaignType:
    id: strawberry.ID
    name: str
    description: str
    status: CampaignStatus
    created_at: str
    updated_at: str

    @staticmethod
    def from_model(campaign: Campaign) -> "CampaignType":
        return CampaignType(
            id=strawberry.ID(str(campaign.id)),
            name=campaign.name,
            description=campaign.description,
            status=CampaignStatus(campaign.status),
            created_at=campaign.created_at.isoformat(),
            updated_at=campaign.updated_at.isoformat(),
        )


@strawberry.type
class CampaignPage:
    items: list[CampaignType]
    total_count: int
    page: int
    per_page: int


@strawberry.type
class CampaignQueries:
    @strawberry.field
    def campaigns(
        self,
        page: int = 1,
        per_page: int = 20,
    ) -> CampaignPage:
        if page < 1:
            page = 1
        if per_page < 1 or per_page > MAX_PER_PAGE:
            per_page = 20
        qs = CampaignService.list_campaigns()
        total = qs.count()
        offset = (page - 1) * per_page
        items = qs[offset : offset + per_page]
        return CampaignPage(
            items=[CampaignType.from_model(c) for c in items],
            total_count=total,
            page=page,
            per_page=per_page,
        )

    @strawberry.field
    def campaign(self, id: strawberry.ID) -> CampaignType | None:
        try:
            campaign_id = uuid.UUID(str(id))
        except ValueError:
            return None
        campaign = CampaignService.get_campaign_by_id(campaign_id)
        if campaign is None:
            return None
        return CampaignType.from_model(campaign)


@strawberry.type
class CampaignMutations:
    @strawberry.mutation
    def create_campaign(self, input: CampaignInput) -> CampaignType:
        try:
            campaign = CampaignService.create_campaign(
                name=input.name,
                description=input.description,
            )
        except ValidationError as e:
            raise GraphQLError(str(e)) from e
        return CampaignType.from_model(campaign)

    @strawberry.mutation
    def update_campaign(
        self,
        id: strawberry.ID,
        input: CampaignUpdateInput,
    ) -> CampaignType | None:
        try:
            campaign_id = uuid.UUID(str(id))
        except ValueError:
            return None
        try:
            name_str = input.name
            desc_str = input.description
            status_val = input.status.value if input.status is not None else None
            campaign = CampaignService.update_campaign(
                campaign_id=campaign_id,
                name=name_str,
                description=desc_str,
                status=status_val,
            )
        except ValidationError as e:
            raise GraphQLError(str(e)) from e
        if campaign is None:
            return None
        return CampaignType.from_model(campaign)

    @strawberry.mutation
    def delete_campaign(self, id: strawberry.ID) -> bool:
        try:
            campaign_id = uuid.UUID(str(id))
        except ValueError:
            return False
        return CampaignService.soft_delete_campaign(campaign_id)
