# Plan — F-024: Authentication & Access Control

## Meta
- **From:** Tech Lead
- **To:** Builder
- **Date:** 2026-06-25
- **Branch:** `feat/F-024-auth-access-control`

## Overview

Add JWT-based authentication, a User model, login/register/refresh mutations, per-resolver authorization checks, and WebSocket authentication. Currently all GraphQL endpoints and WebSocket connections are publicly accessible.

## Architecture Decision

**JWT with `SimpleJWT`** (via `djangorestframework-simplejwt`) over alternatives:
- `strawberry-django-jwt` — heavy, opinionated, less maintained
- Session-based — doesn't work well for GraphQL + mobile clients
- OAuth — overkill for a demo challenge

Authentication is a **Strawberry extension** that reads the `Authorization: Bearer <token>` header, validates the JWT, and injects the user into the GraphQL context. No DRF dependency needed — we use PyJWT directly for token encode/decode and keep it lightweight.

## Dependencies to Add

```toml
dependencies = [
    "PyJWT>=2.10,<3",
]
```

No new Django apps — authentication lives in a new `backend/apps/auth/` app.

## Implementation Steps

### Step 1: Create `apps/auth` Django app
- `apps/auth/__init__.py`
- `apps/auth/apps.py` — app config, register in INSTALLED_APPS
- `apps/auth/schema.py` — GraphQL mutations + types
- `apps/auth/services.py` — token creation, validation, user CRUD
- `apps/auth/exceptions.py` — custom auth exceptions
- `apps/auth/tests/__init__.py`
- `apps/auth/tests/test_auth_mutations.py`

### Step 2: User model (use Django's built-in `AbstractUser`)
Django's `django.contrib.auth.models.User` is already in `INSTALLED_APPS`. We use it directly — no custom model needed for now. Add an `owner` field (FK to User) on Campaign and ContentPiece models.

### Step 3: Add `owner` FK to Campaign and ContentPiece
- `Campaign.owner = ForeignKey(User, on_delete=CASCADE, null=True)` — nullable for backward compat
- `ContentPiece.owner` — inherits from campaign ownership (or set explicitly)
- Migration generated for both

### Step 4: JWT token service (`apps/auth/services.py`)
- `create_tokens(user)` — returns access + refresh token pair
- `decode_token(token)` — validates and decodes, returns user or raises
- Access token expiry: 15 minutes
- Refresh token expiry: 7 days

### Step 5: GraphQL mutations (`apps/auth/schema.py`)
```
registerUser(email: String!, password: String!) → AuthPayload { user, accessToken, refreshToken }
login(email: String!, password: String!) → AuthPayload { user, accessToken, refreshToken }
refreshToken(refreshToken: String!) → TokenPayload { accessToken }
```
- `AuthPayload`: `user: UserType`, `accessToken: String`, `refreshToken: String`
- `UserType`: `id: ID`, `email: String`, `createdAt: String`

### Step 6: Auth context + Strawberry extension
Create `backend/apps/auth/extensions.py`:
```python
class AuthExtension(SchemaExtension):
    def on_request_start(self):
        request = self.execution_context.context.get("request")
        token = extract_bearer_token(request)
        if token:
            user = decode_token(token)
            self.execution_context.context["user"] = user
        else:
            self.execution_context.context["user"] = None
```

Create `backend/apps/auth/utils.py`:
```python
def get_user_or_error(info: Info) -> User:
    user = info.context.get("user")
    if user is None:
        raise GraphQLError("Authentication required")
    return user
```

### Step 7: Wire auth extension into schema
In `config/schema.py`:
```python
from apps.auth.extensions import AuthExtension
schema = strawberry.Schema(query=Query, mutation=Mutation, extensions=[AuthExtension()])
```

### Step 8: Add auth checks to every resolver
All existing resolvers need `get_user_or_error(info)` at the top, and queries/mutations must filter by `owner=user`.

- `campaigns/schema.py`: `campaigns()` filters by owner, `campaign()` checks ownership
- `campaigns/services.py`: `create_campaign()` takes `user`, `list_campaigns()` filters by user
- `content/schema.py`: same pattern — filter by campaign ownership
- `ai/schema.py`: check ownership before generating/translating
- `reviews/schema.py`: check ownership before reviewing

### Step 9: WebSocket authentication
In `ws/consumers.py`, modify `connect()`:
```python
async def connect(self) -> None:
    token = self.scope["query_string"].decode().replace("token=", "")
    user = await decode_token_async(token)
    if user is None:
        await self.close(code=4001)
        return
    self.scope["user"] = user
    ...
```

Frontend WebSocket URL changes to: `ws://.../ws/content/{id}/?token={jwt}`

### Step 10: Frontend auth hooks
- `frontend/src/hooks/useAuth.ts` — stores token in memory, provides login/register/logout
- `frontend/src/services/api.ts` — add `Authorization: Bearer <token>` interceptor
- `frontend/src/services/websocket.ts` — pass token as query param on connect
- Login page at `/login` and Register page at `/register` (or modals on dashboard)

### Step 11: Per-resolver permission granularity
- Admin-only: `deleteCampaign`, `deleteContentPiece` (or restrict to owner)
- Owner-only: `updateCampaign`, `updateContent`, `reviewContent`, `generateDraft`, `translateContent`
- Read-only for own campaigns: `campaigns`, `campaign`, `contentPieces`, `content`

### Step 12: Migrations
- `auth` app migration (no model — just app registration)
- Campaign migration: add `owner` FK
- ContentPiece migration: add `owner` FK

## API Contract

### Mutations

```graphql
mutation RegisterUser($email: String!, $password: String!) {
  registerUser(email: $email, password: $password) {
    user { id email createdAt }
    accessToken
    refreshToken
  }
}

mutation Login($email: String!, $password: String!) {
  login(email: $email, password: $password) {
    user { id email createdAt }
    accessToken
    refreshToken
  }
}

mutation RefreshToken($refreshToken: String!) {
  refreshToken(refreshToken: $refreshToken) {
    accessToken
  }
}
```

### Error Responses
- `401`: `"Authentication required"` — no token or invalid token
- `403`: `"You do not have permission to perform this action"` — wrong owner
- `400`: `"Invalid email or password"` — login failure
- `400`: `"Email already registered"` — duplicate registration

## Test Plan

| Test | Type | What it covers |
|------|------|----------------|
| `test_register_user` | unit | Creates user, returns tokens, user has correct email |
| `test_register_duplicate_email` | unit | Raises GraphQLError |
| `test_login_valid` | unit | Returns tokens for valid credentials |
| `test_login_invalid_password` | unit | Raises GraphQLError |
| `test_refresh_token_valid` | unit | Returns new access token |
| `test_refresh_token_expired` | unit | Raises GraphQLError |
| `test_mutation_needs_auth` | unit | createCampaign without token returns error |
| `test_query_filters_by_owner` | integration | User A cannot see User B's campaigns |
| `test_campaign_owner_set_on_create` | integration | Created campaign has correct owner |
| `test_ws_connect_without_token` | unit | Connection rejected with code 4001 |
| `test_ws_connect_with_valid_token` | unit | Connection accepted |
| All existing 130 tests | regression | Auth middleware doesn't break existing flows |

## Documentation Updates

- `docs/adrs/ADR-007-authentication.md`: New ADR — JWT choice, token flow, WS auth
- `README.md`: Add Authentication section, register/login mutations to GraphQL reference
- `frontend/README.md`: Add auth flow documentation

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Breaking existing resolvers | Medium | Add `owner=None` default on FK, make auth optional in dev mode |
| Token storage on frontend | Medium | Store in memory (not localStorage), re-fetch on page reload |
| WebSocket auth token expiry | Low | Frontend reconnects with fresh token, server rejects expired tokens gracefully |
