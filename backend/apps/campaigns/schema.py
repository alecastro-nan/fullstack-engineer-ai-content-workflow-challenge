import strawberry


@strawberry.type
class Campaign:
    id: strawberry.ID
    name: str
    description: str
    status: str
    created_at: str
    updated_at: str
