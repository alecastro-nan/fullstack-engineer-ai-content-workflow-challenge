import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.reviews.models import StateHistory

logger = logging.getLogger(__name__)


@receiver(post_save, sender=StateHistory)
def broadcast_state_change(
    sender: type[StateHistory],
    instance: StateHistory,
    created: bool,
    **kwargs: object,
) -> None:
    if not created:
        return

    content_piece = instance.content_piece
    group_name = f"content_{content_piece.id}"

    channel_layer = get_channel_layer()
    if channel_layer is None:
        logger.warning("No channel layer configured — skipping WebSocket broadcast")
        return

    payload: dict[str, object] = {
        "contentId": str(content_piece.id),
        "campaignId": str(content_piece.campaign_id),
        "oldState": instance.from_state,
        "newState": instance.to_state,
        "action": instance.action,
        "timestamp": instance.created_at.isoformat(),
    }

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "state.change",
            "payload": payload,
        },
    )
