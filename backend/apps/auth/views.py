import logging
from typing import Any, cast

from django.http import HttpRequest, HttpResponse, HttpResponseBase
from strawberry.django.context import StrawberryDjangoContext
from strawberry.django.views import GraphQLView

from apps.auth.exceptions import InvalidToken

logger = logging.getLogger(__name__)


class AuthGraphQLView(GraphQLView):
    def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponseBase:
        if request.method == "POST" and request.content_type != "application/json":
            return HttpResponse(
                "Unsupported Media Type. Content-Type must be application/json",
                status=415,
                content_type="text/plain",
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context(self, request: HttpRequest, response: HttpResponse) -> StrawberryDjangoContext:  # type: ignore[override]
        from apps.auth.services import decode_token
        from apps.auth.utils import extract_bearer_token

        user = None
        token = extract_bearer_token(request)
        if token:
            try:
                user = decode_token(token)
            except InvalidToken:
                logger.warning("Invalid token provided")

        context = StrawberryDjangoContext(request=request, response=response)
        cast(Any, context).user = user
        return context
