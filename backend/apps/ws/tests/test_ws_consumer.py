import pytest
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator

from apps.ws.consumers import ContentConsumer


@pytest.mark.django_db
class TestContentConsumer:
    def _make_communicator(
        self,
        content_id: str = "123e4567-e89b-12d3-a456-426614174000",
    ) -> WebsocketCommunicator:
        communicator = WebsocketCommunicator(
            ContentConsumer.as_asgi(),
            f"/ws/content/{content_id}/",
        )
        communicator.scope["url_route"] = {
            "kwargs": {"content_id": content_id},
            "args": [],
        }
        return communicator

    async def test_connect_and_receive_ack(self) -> None:
        communicator = self._make_communicator()
        connected, _ = await communicator.connect()
        assert connected

        response = await communicator.receive_json_from()
        assert response["type"] == "connection.ack"
        assert response["contentId"] == "123e4567-e89b-12d3-a456-426614174000"

        await communicator.disconnect()

    async def test_receive_state_change_via_channel_layer(self) -> None:
        communicator = self._make_communicator()
        await communicator.connect()
        await communicator.receive_json_from()

        channel_layer = get_channel_layer()
        group_name = "content_123e4567-e89b-12d3-a456-426614174000"

        await channel_layer.group_send(group_name, {
            "type": "state.change",
            "payload": {
                "contentId": "123e4567-e89b-12d3-a456-426614174000",
                "campaignId": "abc-456",
                "oldState": "draft",
                "newState": "suggested_by_ai",
                "action": "GENERATE_AI",
                "timestamp": "2025-01-01T00:00:00+00:00",
            },
        })

        response = await communicator.receive_json_from()
        assert response["type"] == "state.change"
        assert response["contentId"] == "123e4567-e89b-12d3-a456-426614174000"
        assert response["oldState"] == "draft"
        assert response["newState"] == "suggested_by_ai"
        assert response["action"] == "GENERATE_AI"

        await communicator.disconnect()

    async def test_disconnect_does_not_crash(self) -> None:
        communicator = self._make_communicator()
        await communicator.connect()
        await communicator.receive_json_from()
        await communicator.disconnect()
