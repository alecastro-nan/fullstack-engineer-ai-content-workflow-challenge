from django.contrib import admin

from apps.campaigns.models import Campaign


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "created_at", "is_deleted"]
    list_filter = ["status", "is_deleted"]
    search_fields = ["name"]
