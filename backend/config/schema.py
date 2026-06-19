import strawberry

from apps.campaigns.schema import CampaignMutations, CampaignQueries


@strawberry.type
class Query(CampaignQueries):
    @strawberry.field
    def health(self) -> str:
        return "ok"


@strawberry.type
class Mutation(CampaignMutations):
    @strawberry.mutation
    def ping(self) -> str:
        return "pong"


schema = strawberry.Schema(query=Query, mutation=Mutation)
