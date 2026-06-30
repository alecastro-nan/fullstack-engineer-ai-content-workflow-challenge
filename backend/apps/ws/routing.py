from django.urls import re_path

from apps.ws.consumers import ContentConsumer

websocket_urlpatterns = [
    re_path(
        r"ws/content/(?P<content_id>[a-f0-9\-]+)/$",
        ContentConsumer.as_asgi(),  # type: ignore[arg-type]
    ),
]
