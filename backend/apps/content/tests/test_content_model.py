import uuid

import pytest
from django.core.exceptions import ValidationError

from apps.campaigns.models import Campaign
from apps.campaigns.services import CampaignService
from apps.content.models import ContentPiece
from apps.content.services import ContentPieceService


@pytest.fixture
def campaign() -> Campaign:
    return CampaignService.create_campaign(name="Test Campaign", description="For content tests")


@pytest.mark.django_db
class TestContentPieceService:
    def test_create_content_piece(self, campaign: Campaign) -> None:
        piece = ContentPieceService.create_content_piece(
            campaign_id=campaign.id,
            headline="Test Headline",
            description="A test piece",
            body="Body content",
            language="en",
        )
        assert piece.headline == "Test Headline"
        assert piece.description == "A test piece"
        assert piece.body == "Body content"
        assert piece.language == "en"
        assert piece.state == ContentPiece.State.DRAFT
        assert piece.is_deleted is False
        assert piece.campaign.pk == campaign.id
        assert piece.id is not None

    def test_create_content_piece_strips_whitespace(self, campaign: Campaign) -> None:
        piece = ContentPieceService.create_content_piece(
            campaign_id=campaign.id,
            headline="  Spaced Headline  ",
            description="  Desc  ",
            body="  Body  ",
            language="  EN  ",
        )
        assert piece.headline == "Spaced Headline"
        assert piece.description == "Desc"
        assert piece.body == "Body"
        assert piece.language == "EN"

    def test_create_content_piece_rejects_empty_headline(self, campaign: Campaign) -> None:
        with pytest.raises(ValidationError):
            ContentPieceService.create_content_piece(
                campaign_id=campaign.id,
                headline="",
            )

    def test_create_content_piece_rejects_blank_headline(self, campaign: Campaign) -> None:
        with pytest.raises(ValidationError):
            ContentPieceService.create_content_piece(
                campaign_id=campaign.id,
                headline="   ",
            )

    def test_create_content_piece_rejects_headline_too_long(self, campaign: Campaign) -> None:
        with pytest.raises(ValidationError):
            ContentPieceService.create_content_piece(
                campaign_id=campaign.id,
                headline="x" * 256,
            )

    def test_create_content_piece_nonexistent_campaign(self) -> None:
        with pytest.raises(ValidationError):
            ContentPieceService.create_content_piece(
                campaign_id=uuid.uuid4(),
                headline="Orphan",
            )

    def test_get_content_piece_by_id(self, campaign: Campaign) -> None:
        created = ContentPieceService.create_content_piece(
            campaign_id=campaign.id,
            headline="Find Me",
        )
        found = ContentPieceService.get_content_piece_by_id(created.id)
        assert found is not None
        assert found.id == created.id
        assert found.headline == "Find Me"

    def test_get_content_piece_by_id_returns_none_for_missing(self) -> None:
        result = ContentPieceService.get_content_piece_by_id(uuid.uuid4())
        assert result is None

    def test_get_content_piece_by_id_returns_none_for_deleted(self, campaign: Campaign) -> None:
        created = ContentPieceService.create_content_piece(
            campaign_id=campaign.id,
            headline="Delete Me",
        )
        ContentPieceService.soft_delete_content_piece(created.id)
        result = ContentPieceService.get_content_piece_by_id(created.id)
        assert result is None

    def test_list_content_pieces(self, campaign: Campaign) -> None:
        ContentPieceService.create_content_piece(campaign_id=campaign.id, headline="A")
        ContentPieceService.create_content_piece(campaign_id=campaign.id, headline="B")
        pieces = ContentPieceService.list_content_pieces(campaign_id=campaign.id)
        assert pieces.count() >= 2

    def test_list_content_pieces_other_campaign(self, campaign: Campaign) -> None:
        c2 = CampaignService.create_campaign(name="Other")
        ContentPieceService.create_content_piece(campaign_id=campaign.id, headline="In A")
        ContentPieceService.create_content_piece(campaign_id=c2.id, headline="In B")
        pieces_a = ContentPieceService.list_content_pieces(campaign_id=campaign.id)
        assert all(p.campaign.pk == campaign.id for p in pieces_a)
        pieces_b = ContentPieceService.list_content_pieces(campaign_id=c2.id)
        assert all(p.campaign.pk == c2.id for p in pieces_b)

    def test_list_content_pieces_excludes_deleted(self, campaign: Campaign) -> None:
        ContentPieceService.create_content_piece(campaign_id=campaign.id, headline="Visible")
        c2 = ContentPieceService.create_content_piece(campaign_id=campaign.id, headline="Hidden")
        ContentPieceService.soft_delete_content_piece(c2.id)
        pieces = ContentPieceService.list_content_pieces(campaign_id=campaign.id)
        names = [p.headline for p in pieces]
        assert "Visible" in names
        assert "Hidden" not in names

    def test_update_content_piece(self, campaign: Campaign) -> None:
        created = ContentPieceService.create_content_piece(
            campaign_id=campaign.id,
            headline="Old",
            description="Old desc",
        )
        updated = ContentPieceService.update_content_piece(
            content_id=created.id,
            headline="New",
            description="New desc",
        )
        assert updated is not None
        assert updated.headline == "New"
        assert updated.description == "New desc"

    def test_update_content_piece_rejects_empty_headline(self, campaign: Campaign) -> None:
        created = ContentPieceService.create_content_piece(
            campaign_id=campaign.id,
            headline="Keep",
        )
        with pytest.raises(ValidationError):
            ContentPieceService.update_content_piece(
                content_id=created.id,
                headline="",
            )

    def test_update_content_piece_nonexistent(self) -> None:
        result = ContentPieceService.update_content_piece(
            content_id=uuid.uuid4(),
            headline="Ghost",
        )
        assert result is None

    def test_soft_delete_content_piece(self, campaign: Campaign) -> None:
        created = ContentPieceService.create_content_piece(
            campaign_id=campaign.id,
            headline="To Delete",
        )
        result = ContentPieceService.soft_delete_content_piece(created.id)
        assert result is True
        deleted = ContentPiece.objects.get(id=created.id)
        assert deleted.is_deleted is True

    def test_soft_delete_nonexistent(self) -> None:
        result = ContentPieceService.soft_delete_content_piece(uuid.uuid4())
        assert result is False

    def test_content_str(self, campaign: Campaign) -> None:
        piece = ContentPieceService.create_content_piece(
            campaign_id=campaign.id,
            headline="Display Name",
        )
        assert str(piece) == "Display Name"
