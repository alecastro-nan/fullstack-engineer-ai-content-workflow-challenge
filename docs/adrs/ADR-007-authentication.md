# ADR-007: Authentication & Access Control

## Status
Accepted

## Context
The platform needs to authenticate users and authorize API access. With 23 existing GraphQL endpoints and WebSocket connections, we needed an auth mechanism that:
1. Works with Strawberry GraphQL's request lifecycle
2. Supports WebSocket token authentication
3. Is stateless (no server-side sessions) for horizontal scaling
4. Can be toggled off for development/demo without code changes

We evaluated several approaches for integrating JWT auth with Strawberry Django.

## Decision
We use **PyJWT** (direct JWT encoding/decoding) with a **custom `GraphQLView` subclass** that decodes tokens in `get_context()` and injects the authenticated user into the Strawberry context. Tokens are signed with Django's `SECRET_KEY` — no additional secrets or third-party JWT libraries required.

### Architecture
```
Client                         Server
  │       POST /graphql          │
  │  Authorization: Bearer JWT   │
  └─────────────────────────────>│
                                 │  AuthGraphQLView.get_context()
                                 │    └─ decode JWT → User
                                 │    └─ inject into context.user
                                 │
                                 │  Resolver reads info.context.user
                                 │  get_user_or_error() → User or 401
                                 │
  │    { "data": {...} }         │
  <─────────────────────────────┘
```

### Token Design
- **Access token**: 15-minute expiry, signed with `HS256`, contains `user_id`, `email`, `type: "access"`
- **Refresh token**: 7-day expiry, signed with `HS256`, contains `user_id`, `email`, `type: "refresh"`
- Both tokens are stateless (no server-side blacklist) — acceptable for a demo/scoping exercise
- `decode_token()` verifies signature, expiry, and token type, then fetches user from DB

### Auth Enforcement
| Layer | Mechanism | File |
|---|---|---|
| GraphQL resolver | `get_user_or_error(info)` raises `GraphQLError("Authentication required")` | `apps/auth/utils.py` |
| Campaign owner filter | `piece.campaign.owner != user` returns `None` or `[]` instead of raising | `apps/reviews/schema.py`, `apps/content/schema.py` |
| WebSocket | Token passed as `?token=` query param, decoded in `connect()` | `apps/ws/consumers.py` |

### Why custom GraphQLView instead of SchemaExtension?
Strawberry v0.317.x `SchemaExtension` exposes `on_operation`, `on_execute`, `on_parse`, `on_validate` hooks — but **not** `on_request_start`. Extensions operate within the GraphQL execution pipeline and don't have access to the raw Django `HttpRequest` for header extraction. A custom `GraphQLView` overriding `get_context()` is the standard pattern for injecting per-request data in Strawberry Django.

### Models
- `Campaign.owner` — ForeignKey to `auth.User` (nullable, `on_delete=PROTECT` for data integrity)
- `ContentPiece` ownership is derived via `content_piece.campaign.owner` (no direct FK, prevents inconsistent owner assignments)

### Auth Mutations
- `registerUser(email, password)` → `AuthPayload { user, accessToken, refreshToken }`
- `login(email, password)` → `AuthPayload { user, accessToken, refreshToken }`
- `refreshToken(refreshToken)` → `TokenPayload { accessToken }`

### Environment toggle
`AUTH_REQUIRED` setting (default `True`) makes auth optional — when `False`, `get_user_or_error()` returns `None` instead of raising.

## Consequences

### Positive
- No additional dependencies beyond PyJWT (which is already a transitive dependency of Strawberry)
- Token signing reuses existing `DJANGO_SECRET_KEY` — no new env vars
- Works transparently with Django test client via `HTTP_AUTHORIZATION` header
- Ownership-based access control prevents users from accessing or modifying other users' campaigns
- WebSocket auth uses the same JWT tokens as GraphQL API

### Negative
- Tokens cannot be revoked server-side (no blacklist) — acceptable for demo
- `SECRET_KEY` rotation invalidates all tokens (same as Django sessions)
- Database lookup on every authenticated request (to verify user still exists and is active)
- Frontend must manage token storage and refresh flow (not yet implemented in this PR)

## Alternatives Considered
- **`strawberry-django-jwt`**: Rejected — unnecessary dependency for simple JWT auth; more opinionated than needed
- **Django REST Framework + SimpleJWT**: Rejected — would couple auth to REST framework; we use GraphQL
- **Session-based auth (Django `AuthenticationMiddleware`)**: Rejected — requires CSRF tokens for GraphQL, doesn't work with WebSocket without additional setup
- **SchemaExtension with `on_request_start`**: Rejected — hook doesn't exist in Strawberry v0.317.x; extension API doesn't have access to `HttpRequest`
- **AuthMiddleware on ASGI scope**: Rejected — would require intercepting HTTP requests at the ASGI level, which is heavier than a view-level override

## References
- Implementation: `backend/apps/auth/` (views.py, services.py, schema.py, utils.py, test_utils.py)
- GraphQL view override: `backend/config/urls.py` (uses `AuthGraphQLView`)
- Migration: `backend/apps/campaigns/migrations/0002_add_owner_fk.py`
- Plan: `agentic/runs/F-024-auth-access-control/plan.md`
- PyJWT: https://pyjwt.readthedocs.io/
