import uuid

from django.db import models

from apps.content.models import ContentPiece


class StateHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_piece = models.ForeignKey(
        ContentPiece,
        on_delete=models.PROTECT,
        related_name="state_history",
    )
    from_state = models.CharField(max_length=20)
    to_state = models.CharField(max_length=20)
    action = models.CharField(max_length=30)
    feedback = models.TextField(blank=True, default="", max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "state_history"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["content_piece", "-created_at"],
                name="idx_history_content_created",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.content_piece_id}: {self.from_state} → {self.to_state} ({self.action})"  # type: ignore[attr-defined]
