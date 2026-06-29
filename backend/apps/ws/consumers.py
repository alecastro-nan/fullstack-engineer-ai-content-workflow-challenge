import json
import logging
import uuid
from typing import Any, cast
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

from apps.auth.services import decode_token_async
from apps.content.services import ContentPieceService

logger = logging.getLogger(__name__)


class ContentConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.content_id: str = ""
        self.group_name: str = ""

    async def connect(self) -> None:
        token = self._extract_token()
        if not token:
            await self.close(code=4001)
            return

        user = await decode_token_async(token)
        if user is None:
            await self.close(code=4001)
            return

        if not self._check_origin():
            await self.close(code=4001)
            return

        self.scope["user"] = user  # type: ignore[typeddict-item]

        self.content_id = self.scope["url_route"]["kwargs"]["content_id"]
        self.group_name = f"content_{self.content_id}"

        piece = await sync_to_async(ContentPieceService.get_content_piece_by_id)(
            uuid.UUID(self.content_id)
        )
        if piece is None or piece.campaign.owner != user:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.send_json({
            "type": "connection.ack",
            "contentId": self.content_id,
        })

    def _extract_token(self) -> str | None:
        headers: dict[bytes, bytes] = dict(self.scope.get("headers") or [])
        protocol = headers.get(b"sec-websocket-protocol", b"")
        if protocol:
            return protocol.decode()
        params = parse_qs(self.scope["query_string"].decode())
        values = params.get("token")
        return values[0] if values else None

    def _check_origin(self) -> bool:
        headers: dict[bytes, bytes] = dict(self.scope.get("headers") or [])
        origin = headers.get(b"origin", b"").decode()
        if not origin:
            return True
        allowed = cast(str, getattr(settings, "FRONTEND_URL", ""))
        return origin == allowed

    async def disconnect(self, close_code: int) -> None:
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_json(self, content: dict[str, object]) -> None:
        await super().send(text_data=json.dumps(content))

    async def state_change(self, event: dict[str, Any]) -> None:
        payload = event.get("payload", {})
        await self.send_json({
            "type": "state.change",
            "contentId": payload.get("contentId", ""),
            "campaignId": payload.get("campaignId", ""),
            "oldState": payload.get("oldState", ""),
            "newState": payload.get("newState", ""),
            "action": payload.get("action", ""),
            "timestamp": payload.get("timestamp", ""),
        })
