# Plan — F-030: Authentication & WebSocket Hardening

## Meta
- **Task ID:** F-030
- **Branch:** `feat/F-030-auth-ws-hardening`
- **Dependencies:** None
- **Est. time:** ~2h
- **Reviewers:** @code-reviewer, @security-reviewer

## Overview

Address 13 backend security issues from the PR #1 audit. Organized into 4 sub-groups that can be implemented sequentially:

1. Token & Authentication Security (6 items, ~45min)
2. WebSocket Security (2 items, ~20min)
3. Rate Limiting (3 items, ~30min)
4. Thread Safety & Provider Config (2 items, ~20min)

## Sub-group 1: Token & Authentication Security

### Changes needed

#### 1a. JWT cookie storage (C-2)
**File:** `frontend/src/services/api.ts`
- Current: reads `access_token` from `localStorage`, attaches as `Authorization: Bearer` header
- Target: server sets httpOnly Secure SameSite=Strict cookie on login/register; client reads cookie automatically on same-origin requests
- Frontend api.ts: remove `localStorage.getItem('access_token')` logic; let browser send cookie
- Backend auth/services.py: `create_access_token` sets cookie in response (needs access to response object — may need to restructure mutation to set cookie via GraphQL view)

**Alternative approach** (less invasive): Keep Bearer header but store token in a short-lived in-memory variable (React state/context) instead of localStorage. This avoids cookie restructuring while still preventing XSS-based token theft.

**Decision:** Use httpOnly cookie approach — it's the proper fix per security review. Implement via custom GraphQL view that sets cookies on login/register/refresh responses.

#### 1b. Token version field (C-4)
**File:** `backend/apps/auth/services.py`, require migration on User model
- Add `token_version` IntegerField to User model (default=0)
- Include `token_version` in JWT payload
- In `decode_token()`, verify `payload["token_version"] == user.token_version`
- In password change, increment `user.token_version += 1` (invalidates all existing tokens)

#### 1c. Force logout on password change (C-4)
Same mechanism as 1b — token_version increment implicitly logs out other sessions.

#### 1d. Separate JWT_SIGNING_KEY (H-1)
**File:** `backend/config/settings/base.py`, `backend/apps/auth/services.py`
- Add `JWT_SIGNING_KEY` env var to base.py
- Update `_get_jwt_secret()` to use `settings.JWT_SIGNING_KEY` with fallback to `SECRET_KEY` (for backward compat)
- Update `.env.example` to document `JWT_SIGNING_KEY`

#### 1e. Refresh token rotation (H-8)
**File:** `backend/apps/auth/services.py`
- In `refresh_access_token()`, decode the old refresh token first
- Issue new refresh token alongside new access token
- The old refresh token is NOT invalidated server-side (stateless), but since a new one is issued, the old one is effectively abandoned
- **Stronger fix:** Redis-backed token blacklist or a `refresh_token_hash` field on User to enforce single-use

#### 1f. Remove email from JWT payload (M-1)
**File:** `backend/apps/auth/services.py`
- Remove `"email": user.email` from both access and refresh token payloads
- Keep `user_id` only — look up user from DB when needed

#### 1g. Generic registration error (M-3)
**File:** `backend/apps/auth/services.py`
- Change `EmailAlreadyRegistered("Email already registered")` to a generic `ValidationError("Registration failed")`
- Update the exception class or message in `register_user()` service method

### Files touched
- `backend/apps/auth/services.py`
- `backend/apps/auth/models.py` (add token_version)
- `backend/apps/auth/migrations/0003_token_version.py`
- `backend/apps/auth/schema.py` (cookie setting in mutations)
- `backend/apps/auth/exceptions.py` (if changing exception class)
- `backend/config/settings/base.py` (JWT_SIGNING_KEY)
- `.env.example` (document JWT_SIGNING_KEY)
- `frontend/src/services/api.ts` (cookie removal)
- `frontend/src/services/websocket.ts` (cookie usage)

---

## Sub-group 2: WebSocket Security

### Changes needed

#### 2a. Sec-WebSocket-Protocol auth (C-3)
**File:** `backend/apps/ws/consumers.py`, `frontend/src/services/websocket.ts`
- Remove `?token=` query parameter parsing from consumer.py
- Frontend sends JWT via `Sec-WebSocket-Protocol` header on connection
- Backend reads `self.scope["headers"]` for `Sec-WebSocket-Protocol`, decodes token, authenticates
- If using cookie approach from 1a, the cookie is sent automatically on WebSocket upgrade request — no extra header needed

#### 2b. Origin validation (M-2)
**File:** `backend/apps/ws/consumers.py`
- In `connect()`, read `Origin` header from `self.scope["headers"]`
- Compare against `settings.FRONTEND_URL`
- Reject with close code 4001 if origin doesn't match

### Files touched
- `backend/apps/ws/consumers.py`
- `backend/apps/ws/tests/test_ws_consumer.py`
- `frontend/src/services/websocket.ts`
- `frontend/src/services/websocket.test.ts`

---

## Sub-group 3: Rate Limiting

### Changes needed

#### 3a. Login rate limit (C-7)
**File:** `backend/apps/auth/schema.py`
- Add `django-ratelimit` to dependencies (or use Django's built-in cache-based rate limiting)
- Annotate `login` mutation with `@ratelimit(key='ip', rate='10/m', method='POST')`
- Return `429 Too Many Requests` error via GraphQL

#### 3b. Register rate limit (C-7)
Same approach as 3a, rate='1/m'.

#### 3c. AI endpoint rate limit (C-7)
**File:** `backend/apps/ai/schema.py`
- Rate limit `generateDraft` and `translateContent` per user (20 requests/minute)
- Use `key='user'` or `key='ip'` depending on auth state

### Files touched
- `backend/pyproject.toml` (add django-ratelimit)
- `backend/apps/auth/schema.py`
- `backend/apps/ai/schema.py`
- `backend/config/settings/base.py` (if configuring cache backend)

---

## Sub-group 4: Thread Safety & Provider Config

### Changes needed

#### 4a. Thread-safe fallback (C-5)
**File:** `backend/apps/ai/services.py`, `backend/apps/ai/providers/__init__.py`
- Remove `settings.AI_PROVIDER = fallback_name` mutation
- Update `get_provider()` to accept optional `provider_name` parameter
- Update `_get_fallback_provider()` to pass `provider_name` directly instead of mutating settings

```python
# providers/__init__.py
def get_provider(provider_name: str | None = None) -> AIProvider:
    name = provider_name or getattr(settings, "AI_PROVIDER", "openai")
    ...
```

```python
# services.py
def _get_fallback_provider() -> AIProvider | None:
    primary = getattr(settings, "AI_PROVIDER", "openai")
    fallback_name = "anthropic" if primary == "openai" else "openai"
    try:
        return get_provider(provider_name=fallback_name)
    except ConfigurationError:
        return None
```

#### 4b. AI API timeout (M-5)
**File:** `backend/apps/ai/providers/openai_provider.py`, `backend/apps/ai/providers/anthropic_provider.py`
- OpenAI: pass `timeout=30` to `client.chat.completions.create()`
- Anthropic: pass `timeout=60` to `client.messages.create()`

### Files touched
- `backend/apps/ai/services.py`
- `backend/apps/ai/providers/__init__.py`
- `backend/apps/ai/providers/openai_provider.py`
- `backend/apps/ai/providers/anthropic_provider.py`
- `backend/apps/ai/tests/test_ai_service.py`

---

## Testing Strategy

| Group | Test approach | Key assertions |
|---|---|---|
| 1a | Integration test via GraphQL + http client | Cookie set with httpOnly+Secure; document.cookie doesn't contain token |
| 1b | Unit test | Token with wrong `token_version` raises InvalidToken |
| 1d | Unit test | Token signed with SECRET_KEY fails after JWT_SIGNING_KEY configured |
| 1e | Integration test | Old refresh token returns error on second use |
| 1f | Unit test | Email not present in decoded payload |
| 1g | Integration test | Registration with duplicate email returns generic error |
| 2a | Unit + WS test | WS connects without query param; WS auth via protocol header |
| 2b | Unit test | WS with wrong Origin header gets close code |
| 3a-c | Integration test | 11th login attempt returns 429; 21st AI call returns 429 |
| 4a | Unit test | Concurrent fallback calls use correct provider per request |
| 4b | Unit test | Mock slow response verifies timeout exception |

## Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Cookie-based JWT breaks existing frontend auth flow | Medium | Keep Bearer header as fallback for transition period |
| Rate limiting in tests causes flaky CI | Low | Use Django test-specific cache backend (LOCMEM) |
| django-ratelimit not compatible with Strawberry GraphQL | Low | Use middleware-based approach or manual cache calls |
| Token version migration causes user lockout | Medium | Set token_version=0 default, verify all existing tokens have version 0 in payload |
