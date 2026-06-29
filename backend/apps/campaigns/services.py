import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.utils.html import escape

from apps.campaigns.models import Campaign

MAX_NAME_LENGTH = 255


class CampaignService:
    @staticmethod
    def _validate_name(name: str) -> str:
        stripped = name.strip()
        if not stripped:
            raise ValidationError("Campaign name cannot be empty", code="invalid")
        if len(stripped) > MAX_NAME_LENGTH:
            raise ValidationError(
                f"Campaign name too long (max {MAX_NAME_LENGTH} characters)",
                code="invalid",
            )
        return stripped

    @staticmethod
    def _validate_status(status: str) -> str:
        if status not in Campaign.Status.values:
            raise ValidationError(
                f"Invalid status '{status}'. Valid values: {', '.join(Campaign.Status.values)}",
                code="invalid",
            )
        return status

    @staticmethod
    def create_campaign(name: str, description: str = "", owner: User | None = None) -> Campaign:
        validated_name = CampaignService._validate_name(name)
        return Campaign.objects.create(
            name=escape(validated_name),
            description=escape(description.strip()),
            owner=owner,
        )

    @staticmethod
    def get_campaign_by_id(campaign_id: uuid.UUID) -> Campaign | None:
        try:
            return Campaign.objects.get(id=campaign_id, is_deleted=False)
        except Campaign.DoesNotExist:
            return None

    @staticmethod
    def list_campaigns(user: User | None = None) -> QuerySet[Campaign]:
        qs = Campaign.objects.filter(is_deleted=False)
        if user is not None:
            qs = qs.filter(owner=user)
        return qs.order_by("-created_at")

    @staticmethod
    def update_campaign(
        campaign_id: uuid.UUID,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> Campaign | None:
        campaign = CampaignService.get_campaign_by_id(campaign_id)
        if campaign is None:
            return None
        if name is not None:
            campaign.name = CampaignService._validate_name(name)
        if description is not None:
            campaign.description = escape(description.strip())
        if status is not None:
            campaign.status = CampaignService._validate_status(status)
        campaign.save()
        return campaign

    @staticmethod
    def soft_delete_campaign(campaign_id: uuid.UUID) -> bool:
        campaign = CampaignService.get_campaign_by_id(campaign_id)
        if campaign is None:
            return False
        campaign.is_deleted = True
        campaign.save(update_fields=["is_deleted", "updated_at"])
        return True
