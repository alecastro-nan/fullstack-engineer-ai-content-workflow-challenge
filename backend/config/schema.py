import strawberry

from apps.campaigns.schema import CampaignMutations, CampaignQueries
from apps.content.schema import ContentPieceMutations, ContentPieceQueries


@strawberry.type
class Query(CampaignQueries, ContentPieceQueries):
    @strawberry.field
    def health(self) -> str:
        return "ok"


@strawberry.type
class Mutation(CampaignMutations, ContentPieceMutations):
    @strawberry.mutation
    def ping(self) -> str:
        return "pong"


schema = strawberry.Schema(query=Query, mutation=Mutation)
