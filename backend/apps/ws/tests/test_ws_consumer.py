import uuid

import pytest
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import override_settings

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
        origin: str | None = None,
    ) -> WebsocketCommunicator:
        path = f"/ws/content/{content_id}/"
        headers = {b"origin": origin.encode()} if origin else {}
        if token:
            headers[b"sec-websocket-protocol"] = token.encode()
        communicator = WebsocketCommunicator(
            ContentConsumer.as_asgi(),
            path,
            headers=list(headers.items()),
        )
        communicator.scope["url_route"] = {  # type: ignore[typeddict-unknown-key]
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

    async def test_connect_without_token_rejected(self) -> None:
        from asgiref.sync import sync_to_async

        piece_id, _ = await sync_to_async(_create_test_data)()
        content_id = str(piece_id)
        communicator = self._make_communicator(content_id)
        connected, code = await communicator.connect()
        assert not connected
        assert code == 4001

    async def test_connect_with_invalid_token_rejected(self) -> None:
        from asgiref.sync import sync_to_async

        piece_id, _ = await sync_to_async(_create_test_data)()
        content_id = str(piece_id)
        communicator = self._make_communicator(content_id, token="invalid-token")
        connected, code = await communicator.connect()
        assert not connected
        assert code == 4001

    @override_settings(CORS_ALLOWED_ORIGINS=["http://allowed-origin.com"])
    async def test_connect_with_wrong_origin_rejected(self) -> None:
        from asgiref.sync import sync_to_async

        piece_id, token = await sync_to_async(_create_test_data)()
        content_id = str(piece_id)
        communicator = self._make_communicator(
            content_id,
            token=token,
            origin="http://evil.com",
        )
        connected, code = await communicator.connect()
        assert not connected
        assert code == 4001

    async def test_receive_state_change_via_channel_layer(self) -> None:
        from asgiref.sync import sync_to_async

        piece_id, token = await sync_to_async(_create_test_data)()
        content_id = str(piece_id)
        communicator = self._make_communicator(content_id, token=token)
        await communicator.connect()
        await communicator.receive_json_from()

        channel_layer = get_channel_layer()
        group_name = f"content_{content_id}"

        await channel_layer.group_send(group_name, {  # type: ignore[union-attr]
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
        assert "email" not in response

        await communicator.disconnect()

    async def test_disconnect_does_not_crash(self) -> None:
        from asgiref.sync import sync_to_async

        piece_id, token = await sync_to_async(_create_test_data)()
        content_id = str(piece_id)
        communicator = self._make_communicator(content_id, token=token)
        await communicator.connect()
        await communicator.receive_json_from()
        await communicator.disconnect()
