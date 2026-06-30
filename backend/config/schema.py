import strawberry
from django.conf import settings
from strawberry.extensions import (
    DisableIntrospection,
    MaxAliasesLimiter,
    MaxTokensLimiter,
    QueryDepthLimiter,
)

from apps.ai.schema import AiMutation
from apps.auth.schema import AuthMutation
from apps.campaigns.schema import CampaignMutations, CampaignQueries
from apps.content.schema import ContentPieceMutations, ContentPieceQueries
from apps.reviews.schema import ReviewMutation, ReviewQuery


@strawberry.type
class Query(CampaignQueries, ContentPieceQueries, ReviewQuery):
    @strawberry.field
    def health(self) -> str:
        return "ok"


@strawberry.type
class Mutation(CampaignMutations, ContentPieceMutations, ReviewMutation, AiMutation, AuthMutation):
    @strawberry.mutation
    def ping(self) -> str:
        return "pong"


extensions = [
    lambda: QueryDepthLimiter(max_depth=8),
    lambda: MaxTokensLimiter(max_token_count=1000),
    lambda: MaxAliasesLimiter(max_alias_count=5),
]

if not settings.DEBUG:
    extensions.append(lambda: DisableIntrospection())

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=extensions,
)
