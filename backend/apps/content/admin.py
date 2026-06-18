from django.contrib import admin

from apps.content.models import ContentPiece


@admin.register(ContentPiece)
class ContentPieceAdmin(admin.ModelAdmin):
    list_display = ["headline", "campaign", "language", "state", "created_at"]
    list_filter = ["state", "language", "is_deleted"]
    search_fields = ["headline"]
