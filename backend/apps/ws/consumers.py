import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class ContentConsumer(AsyncWebsocketConsumer):  # type: ignore[misc]
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.content_id: str = ""
        self.group_name: str = ""

    async def connect(self) -> None:
        self.content_id = self.scope["url_route"]["kwargs"]["content_id"]
        self.group_name = f"content_{self.content_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.send_json({
            "type": "connection.ack",
            "contentId": self.content_id,
        })

    async def disconnect(self, close_code: int) -> None:
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_json(self, content: dict[str, object]) -> None:
        await super().send(text_data=json.dumps(content))

    async def state_change(self, event: dict[str, object]) -> None:
        payload = event.get("payload", {})
        msg: dict[str, object] = {"type": "state.change"}
        msg.update(payload)  # type: ignore[call-overload]
        await self.send_json(msg)
