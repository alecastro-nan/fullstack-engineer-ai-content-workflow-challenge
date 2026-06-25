import logging
from typing import Any, cast

from django.http import HttpRequest, HttpResponse
from strawberry.django.context import StrawberryDjangoContext
from strawberry.django.views import GraphQLView

from apps.auth.exceptions import InvalidToken

logger = logging.getLogger(__name__)


class AuthGraphQLView(GraphQLView):
    def get_context(self, request: HttpRequest, response: HttpResponse) -> StrawberryDjangoContext:
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
