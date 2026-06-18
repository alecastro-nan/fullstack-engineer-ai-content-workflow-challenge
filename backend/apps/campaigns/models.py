from django.db import models


class Campaign(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=50, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "campaigns"
        indexes = [
            models.Index(fields=["is_deleted"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return str(self.name)
