from django.db import models


class ContentPiece(models.Model):
    class State(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUGGESTED_BY_AI = "suggested_by_ai", "Suggested by AI"
        REVIEWED = "reviewed", "Reviewed"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, editable=False)
    campaign = models.ForeignKey(
        "campaigns.Campaign",
        on_delete=models.CASCADE,
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
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "content_pieces"
        indexes = [
            models.Index(fields=["campaign"]),
            models.Index(fields=["state"]),
            models.Index(fields=["is_deleted"]),
        ]

    def __str__(self) -> str:
        return str(self.headline)
