import uuid

from django.db import models


class Campaign(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "campaigns"
        indexes = [
            models.Index(fields=["is_deleted", "-created_at"], name="idx_campaigns_list"),
            models.Index(fields=["status"], name="idx_campaigns_status"),
        ]

    def __str__(self) -> str:
        return str(self.name)
