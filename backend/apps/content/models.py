import uuid

from django.db import models


class ContentPiece(models.Model):
    class State(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUGGESTED_BY_AI = "suggested_by_ai", "Suggested by AI"
        REVIEWED = "reviewed", "Reviewed"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        "campaigns.Campaign",
        on_delete=models.PROTECT,
        related_name="content_pieces",
    )
    headline = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    body = models.TextField(blank=True, default="")
    language = models.CharField(max_length=10, default="en")
    state = models.CharField(
        max_length=20,
        choices=State.choices,
        default=State.DRAFT,
    )
    original = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="translations",
        db_index=True,
    )
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "content_pieces"
        indexes = [
            models.Index(
                fields=["campaign", "is_deleted", "-created_at"],
                name="idx_content_campaign_list",
            ),
            models.Index(
                fields=["is_deleted", "-created_at"],
                name="idx_content_deleted_created",
            ),
            models.Index(
                fields=["campaign", "state"],
                name="idx_content_campaign_state",
            ),
        ]

    def __str__(self) -> str:
        return str(self.headline)
