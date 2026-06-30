from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    token_version = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.user.email} (v{self.token_version})"
