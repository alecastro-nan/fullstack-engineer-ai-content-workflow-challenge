import uuid

import pytest
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model

from apps.auth.services import create_tokens
from apps.campaigns.models import Campaign
from apps.content.models import ContentPiece
from apps.ws.consumers import ContentConsumer


def _create_test_data() -> tuple[uuid.UUID, str]:
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username=f"test-user-{uuid.uuid4().hex[:8]}",
        password="testpass",
    )
    campaign = Campaign.objects.create(name="WS Test", owner=user)
    piece = ContentPiece.objects.create(
        campaign=campaign,
        headline="Test",
        description="Test",
    )
    tokens = create_tokens(user)
    return piece.id, tokens["access_token"]


@pytest.mark.django_db(transaction=True)
class TestContentConsumer:
    def _make_communicator(
        self,
        content_id: str,
        token: str | None = None,
    ) -> WebsocketCommunicator:
        path = f"/ws/content/{content_id}/?token={token}" if token else f"/ws/content/{content_id}/"
        communicator = WebsocketCommunicator(
            ContentConsumer.as_asgi(),
            path,
        )
        communicator.scope["url_route"] = {
            "kwargs": {"content_id": content_id},
            "args": [],
        }
        return communicator

    async def test_connect_and_receive_ack(self) -> None:
        from asgiref.sync import sync_to_async

        piece_id, token = await sync_to_async(_create_test_data)()
        content_id = str(piece_id)
        communicator = self._make_communicator(content_id, token=token)
        connected, _ = await communicator.connect()
        assert connected

        response = await communicator.receive_json_from()
        assert response["type"] == "connection.ack"
        assert response["contentId"] == content_id

        await communicator.disconnect()

    async def test_receive_state_change_via_channel_layer(self) -> None:
        from asgiref.sync import sync_to_async

        piece_id, token = await sync_to_async(_create_test_data)()
        content_id = str(piece_id)
        communicator = self._make_communicator(content_id, token=token)
        await communicator.connect()
        await communicator.receive_json_from()

        channel_layer = get_channel_layer()
        group_name = f"content_{content_id}"

        await channel_layer.group_send(group_name, {
            "type": "state.change",
            "payload": {
                "contentId": content_id,
                "campaignId": str(uuid.uuid4()),
                "oldState": "draft",
                "newState": "suggested_by_ai",
                "action": "GENERATE_AI",
                "timestamp": "2025-01-01T00:00:00+00:00",
            },
        })

        response = await communicator.receive_json_from()
        assert response["type"] == "state.change"
        assert response["contentId"] == content_id
        assert response["oldState"] == "draft"
        assert response["newState"] == "suggested_by_ai"
        assert response["action"] == "GENERATE_AI"

        await communicator.disconnect()

    async def test_disconnect_does_not_crash(self) -> None:
        from asgiref.sync import sync_to_async

        piece_id, token = await sync_to_async(_create_test_data)()
        content_id = str(piece_id)
        communicator = self._make_communicator(content_id, token=token)
        await communicator.connect()
        await communicator.receive_json_from()
        await communicator.disconnect()
