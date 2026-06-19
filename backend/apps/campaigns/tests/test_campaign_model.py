import uuid

import pytest
from django.core.exceptions import ValidationError

from apps.campaigns.models import Campaign
from apps.campaigns.services import CampaignService


@pytest.mark.django_db
class TestCampaignService:
    def test_create_campaign(self) -> None:
        campaign = CampaignService.create_campaign(
            name="Test Campaign",
            description="A test campaign",
        )
        assert campaign.name == "Test Campaign"
        assert campaign.description == "A test campaign"
        assert campaign.status == Campaign.Status.ACTIVE
        assert campaign.is_deleted is False
        assert campaign.id is not None

    def test_create_campaign_strips_whitespace(self) -> None:
        campaign = CampaignService.create_campaign(
            name="  Spaced Campaign  ",
            description="  Description  ",
        )
        assert campaign.name == "Spaced Campaign"
        assert campaign.description == "Description"

    def test_create_campaign_rejects_empty_name(self) -> None:
        with pytest.raises(ValidationError):
            CampaignService.create_campaign(name="")

    def test_create_campaign_rejects_blank_name(self) -> None:
        with pytest.raises(ValidationError):
            CampaignService.create_campaign(name="   ")

    def test_create_campaign_rejects_name_too_long(self) -> None:
        with pytest.raises(ValidationError):
            CampaignService.create_campaign(name="x" * 256)

    def test_get_campaign_by_id(self) -> None:
        created = CampaignService.create_campaign(name="Find Me")
        found = CampaignService.get_campaign_by_id(created.id)
        assert found is not None
        assert found.id == created.id
        assert found.name == "Find Me"

    def test_get_campaign_by_id_returns_none_for_missing(self) -> None:
        result = CampaignService.get_campaign_by_id(uuid.uuid4())
        assert result is None

    def test_get_campaign_by_id_returns_none_for_deleted(self) -> None:
        created = CampaignService.create_campaign(name="Delete Me")
        CampaignService.soft_delete_campaign(created.id)
        result = CampaignService.get_campaign_by_id(created.id)
        assert result is None

    def test_list_campaigns(self) -> None:
        CampaignService.create_campaign(name="Alpha")
        CampaignService.create_campaign(name="Bravo")
        campaigns = CampaignService.list_campaigns()
        assert campaigns.count() >= 2

    def test_list_campaigns_excludes_deleted(self) -> None:
        CampaignService.create_campaign(name="Visible")
        c2 = CampaignService.create_campaign(name="Hidden")
        CampaignService.soft_delete_campaign(c2.id)
        campaigns = CampaignService.list_campaigns()
        names = [c.name for c in campaigns]
        assert "Visible" in names
        assert "Hidden" not in names

    def test_update_campaign_name(self) -> None:
        created = CampaignService.create_campaign(name="Old Name")
        updated = CampaignService.update_campaign(
            campaign_id=created.id,
            name="New Name",
        )
        assert updated is not None
        assert updated.name == "New Name"

    def test_update_campaign_rejects_empty_name(self) -> None:
        created = CampaignService.create_campaign(name="Keep")
        with pytest.raises(ValidationError):
            CampaignService.update_campaign(
                campaign_id=created.id,
                name="",
            )

    def test_update_campaign_rejects_invalid_status(self) -> None:
        created = CampaignService.create_campaign(name="Status Test")
        with pytest.raises(ValidationError):
            CampaignService.update_campaign(
                campaign_id=created.id,
                status="invalid_status",
            )

    def test_update_campaign_accepts_valid_status(self) -> None:
        created = CampaignService.create_campaign(name="Archive Me")
        updated = CampaignService.update_campaign(
            campaign_id=created.id,
            status=Campaign.Status.ARCHIVED,
        )
        assert updated is not None
        assert updated.status == Campaign.Status.ARCHIVED

    def test_update_campaign_nonexistent(self) -> None:
        result = CampaignService.update_campaign(
            campaign_id=uuid.uuid4(),
            name="Ghost",
        )
        assert result is None

    def test_soft_delete_campaign(self) -> None:
        created = CampaignService.create_campaign(name="To Delete")
        result = CampaignService.soft_delete_campaign(created.id)
        assert result is True
        deleted = Campaign.objects.get(id=created.id)
        assert deleted.is_deleted is True

    def test_soft_delete_nonexistent(self) -> None:
        result = CampaignService.soft_delete_campaign(uuid.uuid4())
        assert result is False

    def test_campaign_str(self) -> None:
        campaign = CampaignService.create_campaign(name="Display Name")
        assert str(campaign) == "Display Name"
