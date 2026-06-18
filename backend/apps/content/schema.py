import strawberry


@strawberry.type
class ContentPiece:
    id: strawberry.ID
    campaign_id: strawberry.ID
    headline: str
    description: str
    body: str
    language: str
    state: str
    created_at: str
    updated_at: str
