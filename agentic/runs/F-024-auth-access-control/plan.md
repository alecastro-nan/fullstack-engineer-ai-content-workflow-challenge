# Plan — F-024: Authentication & Access Control

## Meta
- **From:** Tech Lead
- **To:** Builder
- **Date:** 2026-06-25
- **Branch:** `feat/F-024-auth-access-control`

## Overview

Add JWT-based authentication, a User model, login/register/refresh mutations, per-resolver authorization checks, and WebSocket authentication. Currently all GraphQL endpoints and WebSocket connections are publicly accessible.

## Architecture Decision

**PyJWT via Strawberry extension** over alternatives:
- `djangorestframework-simplejwt` — pulls in full DRF dependency, unnecessary weight
- `strawberry-django-jwt` — heavy, opinionated, less maintained
- Session-based — doesn't work well for GraphQL + mobile clients
- OAuth — overkill for a demo challenge

Authentication is a **Strawberry extension** that reads the `Authorization: Bearer <token>` header, validates the JWT (signed with `DJANGO_SECRET_KEY`), and injects the user into the GraphQL context. No DRF dependency needed — PyJWT directly handles encode/decode.

**Refresh token tradeoff**: Refresh tokens are stateless JWTs (no server-side blacklist). This means a stolen refresh token is usable for 7 days. Acceptable for a challenge demo — a production system would add a token blacklist table or use opaque tokens.

**Test strategy**: All 130 existing tests must be updated to create a user, generate a token, and pass `Authorization: Bearer <token>` in each GraphQL call.
This is handled via a shared `auth_headers` pytest fixture to minimize per-test changes.

## Dependencies to Add

```toml
dependencies = [
    "PyJWT>=2.10,<3",
]
```

Authentication lives in a new `backend/apps/auth/` app.

## Implementation Steps

### Step 1: Create `apps/auth` Django app
- `apps/auth/__init__.py`
- `apps/auth/apps.py` — app config, register in INSTALLED_APPS
- `apps/auth/schema.py` — GraphQL mutations + types
- `apps/auth/services.py` — token creation, validation, user CRUD
- `apps/auth/exceptions.py` — custom auth exceptions
- `apps/auth/extensions.py` — Strawberry `AuthExtension`
- `apps/auth/utils.py` — `get_user_or_error()` helper, `extract_bearer_token()` helper
- `apps/auth/tests/__init__.py`
- `apps/auth/tests/test_auth_mutations.py`
- `apps/auth/tests/fixtures.py` — shared `auth_headers` fixture for all test files

### Step 2: User model (use Django's built-in `User`)
Django's `django.contrib.auth.models.User` is already in `INSTALLED_APPS`. We use it directly — no custom model needed.

**Existing test strategy**: Create a shared pytest fixture `api_client` in `apps/auth/tests/fixtures.py` that:
1. Creates a `User` via `User.objects.create_user(email="test@example.com", password="testpass123")`
2. Generates a JWT access token via `create_tokens(user)`
3. Returns a `DjangoTestClient` with `HTTP_AUTHORIZATION = f"Bearer {token}"` pre-configured
4. All 130 existing test files import and use `api_client` instead of bare `Client()`

This minimizes changes: replace `def client` with `def api_client` in conftest files, or add a single import in each test file. Target: ~5 minutes of find-and-replace, not 130 individual edits.

### Step 3: Add `owner` FK to Campaign
- `Campaign.owner = ForeignKey(User, on_delete=PROTECT, null=True)` — `PROTECT` prevents cascade-deleting campaigns when a user is removed
- `null=True` for backward compatibility with existing data
- **No `owner` FK on ContentPiece** — ownership is derived via `content.campaign.owner`
- Migration generated for Campaign only

### Step 4: JWT token service (`apps/auth/services.py`)
JWT is signed with `DJANGO_SECRET_KEY` (no new env var needed).
- `create_tokens(user)` — returns access + refresh token pair
- `decode_token(token)` — validates and decodes, returns user or raises `InvalidToken`
- `decode_token_async(token)` — async version for WebSocket consumer
- Access token expiry: 15 minutes
- Refresh token expiry: 7 days
- Token payload: `{"user_id": str(user.id), "email": user.email, "type": "access"|"refresh", "exp": ..., "iat": ...}`

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
In `ws/consumers.py`, modify `connect()` — use proper query string parsing (not fragile `.replace()`):
```python
from urllib.parse import parse_qs

async def connect(self) -> None:
    params = parse_qs(self.scope["query_string"].decode())
    token = (params.get("token") or [None])[0]
    if not token:
        await self.close(code=4001)
        return
    user = await decode_token_async(token)
    if user is None:
        await self.close(code=4001)
        return
    self.scope["user"] = user
    ...
```

Frontend WebSocket URL changes to: `ws://.../ws/content/{id}/?token={jwt}`

### Step 10: Frontend auth wiring (scoped — no UI pages)
- `frontend/src/services/api.ts` — add request interceptor: if a token exists in memory, attach `Authorization: Bearer <token>` header
- `frontend/src/services/websocket.ts` — pass stored token as `?token=` query param on connect
- `frontend/src/hooks/useAuth.ts` — lightweight context that stores `{accessToken, refreshToken}` in a module-level variable (not localStorage), exposes `login()`, `register()`, `logout()`, `getToken()`
- **Deferred to separate task**: Login/Register pages, auth routing guards, login form UI. This keeps F-024 focused on the backend + wiring layer.

### Step 11: Per-resolver permission granularity
- Owner-only: `createCampaign`, `updateCampaign`, `deleteCampaign`, `reviewContent`, `generateDraft`, `translateContent`
- Owner-scoped read: `campaigns()`, `campaign(id)`, `contentPieces()`, `content(id)` — all filter by user's campaigns
- Auth always required: every resolver calls `get_user_or_error(info)` at the top
- Admin-only: none in this task (no admin concept exists yet)

### Step 12: Migrations (order matters — run before step 8)
- `auth` app migration (no model — just app registration)
- Campaign migration: add `owner` FK with `null=True`

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

### New tests (auth app)

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
| `test_invalid_token_format` | unit | Malformed `Authorization` header returns error |

### Shared test fixture strategy (`apps/auth/tests/fixtures.py`)
```python
@pytest.fixture
def auth_headers() -> dict[str, str]:
    user = User.objects.create_user(
        email="test@example.com",
        password="testpass123",
    )
    token = create_access_token(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}
```

Each existing test file adds this fixture and passes it to the client:
```python
# Before
def test_create_campaign(client):
    response = client.post("/graphql", ...)

# After
def test_create_campaign(client, auth_headers):
    response = client.post("/graphql", ..., **auth_headers)
```

### Regression: all existing 130 tests
All existing tests updated to use the `auth_headers` fixture. This is systematic — add fixture import + parameter in every test function. The `api_client` helper fixture (from step 2) bundles `Client()` + `auth_headers` to minimize boilerplate.

### Coverage targets
- `apps/auth/` — ≥90%
- Existing apps — must maintain current coverage (95% backend overall)

## Documentation Updates

- `docs/adrs/ADR-007-authentication.md`: New ADR — JWT with PyJWT, token flow, WS auth, tradeoffs
- `README.md`: Add Authentication section, register/login mutations to GraphQL reference, note about stateless refresh tokens
- `frontend/README.md`: Add auth wiring docs (API interceptor, WS token) — defer UI docs

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Breaking existing resolvers | Medium | Add `owner=None` default on FK, make auth optional in dev mode via `AUTH_REQUIRED` env var (default `True`) |
| 130 existing tests break | High (guaranteed) | Shared `auth_headers` fixture + systematic find-and-replace; verify pytest count stays at 130+ |
| Missing test coverage on auth error paths | Medium | Minimum 11 new auth tests covering success + all error paths |
| Stateless refresh token cannot be revoked | Medium | Document tradeoff in ADR; acceptable for challenge demo |
| Token storage on frontend | Medium | Store in module-level variable (not localStorage), lost on page reload — user re-logs in |
| WebSocket auth token expiry during long session | Low | Frontend reconnects with fresh token; server rejects expired tokens gracefully (close code 4001) |
| ContentPiece owner query performance | Low | Derive via `content.campaign.owner` — no extra query needed since campaign is already loaded in resolvers |
