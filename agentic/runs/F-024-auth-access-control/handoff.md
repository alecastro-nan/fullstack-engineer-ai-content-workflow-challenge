# Handoff — F-024: Authentication & Access Control

## Meta
- **From:** Builder
- **To:** Code Reviewer → Security Reviewer → Done
- **Date:** 2025-06-25

## What was done
- **Auth app**: `apps/auth/` with JWT services, GraphQL mutations, view override
- **Custom AuthGraphQLView**: Overrides `get_context()` to decode JWT from `Authorization` header and inject `user` into Strawberry context
- **JWT tokens**: Access (15min) + Refresh (7day) signed with `DJANGO_SECRET_KEY` via PyJWT
- **Auth mutations**: `registerUser`, `login`, `refreshToken`
- **Owner FK**: `Campaign.owner` (nullable, `on_delete=PROTECT`) with migration
- **Per-resolver auth**: `get_user_or_error()` in all campaign/content/review/ai resolvers
- **Owner filtering**: Queries return only owned resources; mutations check ownership
- **WebSocket auth**: Token via `?token=` query param; ownership check on connect
- **AUTH_REQUIRED toggle**: Dev bypass when `False` (setting + .env.example)
- **Docs**: ADR-007, README updates (auth endpoints, env vars, project structure)

## Tests
- 137/137 passing (includes 9 new auth mutation tests)
- WS tests updated with real DB content + ownership verification
- Review tests updated with `override_settings` + proper AI mock format

## Review findings addressed
- C1: `suppress(Exception)` → catch `InvalidToken` with logging
- C2/H-3: `AUTH_REQUIRED` toggle implemented in `base.py` + `utils.py`
- C3: Missing `Client` imports fixed in 3 test files
- H-1: WebSocket ownership check added
- H-2: `refresh_access_token()` error handling fixed (try/except for JWT + User.DoesNotExist)
- W1: `select_related("campaign__owner")` added to prevent N+1 + async DB access

## Not done / known issues
- Email validation / password validators not invoked in `registerUser` (M-2, M-3 — acceptable for demo)
- Token in WS query string (M-1 — documented in ADR-007, acceptable for local demo)
- Frontend auth UI not implemented (use `make_auth_client` in tests)

## Next actions
1. Code Reviewer: verify fixes applied
2. Security Reviewer: verify fixes applied
3. Merge to feat/agentic-plan

## Artifacts
- Migration: `backend/apps/campaigns/migrations/0002_add_owner_fk.py`
- ADR: `docs/adrs/ADR-007-authentication.md`
- Decision: `agentic/knowledge/decisions/001-auth-custom-graphql-view.md`
