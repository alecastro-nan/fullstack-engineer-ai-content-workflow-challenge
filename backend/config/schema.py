import strawberry

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


schema = strawberry.Schema(query=Query, mutation=Mutation)
