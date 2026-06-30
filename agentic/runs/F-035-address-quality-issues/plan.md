# Plan — F-035: Address 7 remaining medium/major code quality issues from PR review

## Meta

| Field | Value |
|---|---|
| **Task ID** | F-035 |
| **Branch** | `feat/F-035-address-quality-issues` |
| **Base** | `feat/agentic-plan` |
| **Author** | @builder |
| **Reviewers** | @code-reviewer, @security-reviewer, @typescript-reviewer |
| **Est. time** | 45min |
| **Stack** | fullstack (backend + frontend) |

## Overview

Address 7 issues found by subagent review that were never tracked or addressed: 1 major (unhandled promise rejections in CampaignDetail async handlers) and 6 medium (console.error in ErrorBoundary, console.warn in websocket, missing WebSocket send(), broad except Exception in AI providers, rate limiting uses local memory cache, AUTH_REQUIRED toggle bypasses all auth).

### Issues to fix

| ID | Severity | Area | Description |
|---|---|---|---|
| AC-1 | **Major** | Frontend | 6 async handlers in CampaignDetail.tsx (handleCreate, handleUpdate, handleGenerateDraft, handleReview, handleTranslate, handleEditContent) lack try-catch — unhandled promise rejections |
| AC-2 | Medium | Frontend | ErrorBoundary.tsx uses console.error (violates R-014) |
| AC-3 | Medium | Frontend | websocket.ts uses console.warn on malformed messages (violates R-014) |
| AC-4 | Medium | Frontend | WebSocketService has no send() method — consumers cannot send data through WebSocket |
| AC-5 | Medium | Backend | OpenAI + Anthropic providers catch broad `except Exception` instead of specific SDK exceptions |
| AC-6 | Medium | Backend | Rate limiting uses LocMemCache (per-process), doesn't work across workers/containers |
| AC-7 | Medium | Backend | AUTH_REQUIRED=False in production bypasses all auth with no guardrail |

---

## AC-1: Unhandled promise rejections in CampaignDetail async handlers

### Current code

**`frontend/src/pages/CampaignDetail.tsx:133–204`** — 6 handlers, none with error handling:

```typescript
const handleCreate = useCallback(
  async (headline: string, description: string) => {
    if (!id) return;
    const data = await graphqlRequest<...>(CREATE_CONTENT_PIECE_MUTATION, ...);
    setPieces((prev) => [data.createContentPiece, ...prev]);
  },
  [id],
);

const handleUpdate = useCallback(
  async (pieceId: string, headline: string, description: string) => {
    const data = await graphqlRequest<...>(UPDATE_CONTENT_PIECE_MUTATION, ...);
    setPieces((prev) => prev.map((p) => (p.id === pieceId ? data.updateContentPiece : p)));
    setSelectedPieceId(null);
  },
  [],
);

const handleGenerateDraft = useCallback(async (pieceId: string) => {
  const data = await graphqlRequest<...>(GENERATE_DRAFT_MUTATION, ...);
  setPieces((prev) => prev.map((p) => (p.id === pieceId ? data.generateDraft : p)));
}, []);

const handleReview = useCallback(
  async (pieceId: string, action: 'APPROVE' | 'REJECT' | 'REQUEST_EDITS', feedback: string) => {
    const data = await graphqlRequest<...>(REVIEW_CONTENT_MUTATION, ...);
    setPieces((prev) => prev.map((p) => (p.id === pieceId ? data.reviewContent : p)));
    if (action === 'APPROVE') setSelectedPieceId(null);
  },
  [],
);

const handleTranslate = useCallback(
  async (pieceId: string, targetLanguage: string) => {
    const data = await graphqlRequest<...>(TRANSLATE_CONTENT_MUTATION, ...);
    setPieces((prev) => [...prev, data.translateContent]);
  },
  [],
);

const handleEditContent = useCallback(async (pieceId: string) => {
  const data = await graphqlRequest<...>(EDIT_CONTENT_MUTATION, ...);
  setPieces((prev) => prev.map((p) => (p.id === pieceId ? data.editContent : p)));
}, []);
```

### Plan

Each handler needs a try-catch that:
1. Catches the error
2. Sets a user-facing error state (e.g., `error` or `feedbackMessage`)
3. Optionally logs in DEV mode
4. Does not silently swallow

**Approach: shared `handleAsyncError` wrapper**

Create a simple helper or inline each. Simplest: add a `error` state and wrap each handler body:

```typescript
const [error, setError] = useState<string | null>(null);

// Per-handler pattern:
const handleCreate = useCallback(
  async (headline: string, description: string) => {
    try {
      setError(null);
      if (!id) return;
      const data = await graphqlRequest<...>(CREATE_CONTENT_PIECE_MUTATION, ...);
      setPieces((prev) => [data.createContentPiece, ...prev]);
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to create content piece';
      setError(msg);
    }
  },
  [id],
);
```

Apply the same try-catch pattern to all 6 handlers. All catch blocks set `setError(...)` with a human-readable message derived from `e`.

### Files to change

- `frontend/src/pages/CampaignDetail.tsx`

---

## AC-2: console.error in ErrorBoundary

### Current code

**`frontend/src/components/ErrorBoundary.tsx:18–20`**:
```typescript
componentDidCatch(error: Error, info: ErrorInfo) {
  console.error('ErrorBoundary caught:', error, info);
}
```

### Plan

Replace `console.error` with a conditional log gated behind `import.meta.env.DEV`:

```typescript
componentDidCatch(error: Error, info: ErrorInfo) {
  if (import.meta.env.DEV) {
    // eslint-disable-next-line no-console
    console.error('ErrorBoundary caught:', error, info);
  }
}
```

This preserves debug visibility during development while suppressing it in production builds (where Vite strips DEV branches by default).

### Files to change

- `frontend/src/components/ErrorBoundary.tsx`

---

## AC-3: console.warn in websocket.ts

### Current code

**`frontend/src/services/websocket.ts:104`**:
```typescript
console.warn('Malformed WebSocket message:', e);
```

### Plan

Same pattern: gate behind `import.meta.env.DEV`:

```typescript
if (import.meta.env.DEV) {
  // eslint-disable-next-line no-console
  console.warn('Malformed WebSocket message:', e);
}
```

### Files to change

- `frontend/src/services/websocket.ts`

---

## AC-4: Missing WebSocket send() method

### Current code

**`frontend/src/services/websocket.ts:17–182`** — `WebSocketService` class has no `send()` method. Methods present: `subscribe()`, `getStatus()`, `disconnectAll()`, `connect()` (private), `disconnect()` (private), `scheduleReconnect()` (private), `setStatus()` (private).

### Plan

Add a `send()` method that sends a JSON payload over an active WebSocket connection for a given `contentId`:

```typescript
send(contentId: string, data: Record<string, unknown>): void {
  const s = this.connections.get(contentId);
  if (!s?.ws || s.ws.readyState !== WebSocket.OPEN) {
    if (import.meta.env.DEV) {
      console.warn(`WebSocket not open for contentId=${contentId}`);
    }
    return;
  }
  s.ws.send(JSON.stringify(data));
}
```

The method should:
- Accept `contentId` and a payload object
- Look up the connection
- Check `readyState === WebSocket.OPEN`
- `JSON.stringify` and `send`
- Fail silently (with DEV-only log) if not connected — don't throw

### Test implications

Add a test: mock WebSocket, verify `send()` calls `ws.send()` with correct JSON payload, verify it's a no-op when disconnected.

### Files to change

- `frontend/src/services/websocket.ts`
- `frontend/src/services/websocket.test.ts` (or equivalent test file)

---

## AC-5: Broad except Exception in AI providers

### Current code

**`backend/apps/ai/providers/openai_provider.py:55`**:
```python
except Exception as exc:
    error_msg = str(exc).lower()
    if "rate" in error_msg or "429" in error_msg:
        raise RateLimitError(...) from exc
    raise
```

**`backend/apps/ai/providers/anthropic_provider.py:51`** — identical pattern.

### Plan

Narrow the exception handler to specific SDK exceptions. For OpenAI SDK (≥1.0), the relevant exceptions are:

```python
from openai import APIError, RateLimitError as OpenAIRateLimitError

def _call_api(self, prompt: str) -> str:
    try:
        resp = self.client.chat.completions.create(...)
    except OpenAIRateLimitError as exc:
        raise RateLimitError(f"OpenAI rate limit exceeded: {exc}") from exc
    except APIError as exc:
        logger.error("OpenAI API error: %s", exc)
        raise
```

For Anthropic SDK (≥0.40):

```python
from anthropic import APIError, RateLimitError as AnthropicRateLimitError

def _call_api(self, prompt: str) -> str:
    try:
        resp = self.client.messages.create(...)
    except AnthropicRateLimitError as exc:
        raise RateLimitError(f"Anthropic rate limit exceeded: {exc}") from exc
    except APIError as exc:
        logger.error("Anthropic API error: %s", exc)
        raise
```

**Important:** The `RateLimitError` class imported from each SDK is different from the app's `RateLimitError`. Must alias imports to avoid collision.

Also add `import logging` and `logger = logging.getLogger(__name__)` to both files for the fallthrough log.

### Files to change

- `backend/apps/ai/providers/openai_provider.py`
- `backend/apps/ai/providers/anthropic_provider.py`

---

## AC-6: Rate limiting uses local memory cache

### Current code

**`backend/apps/auth/rate_limit.py:1–26`**:
```python
from django.core.cache import cache

def check_rate_limit(key_prefix: str, max_attempts: int, window: int, request: object) -> None:
    ...
    data = cache.get(cache_key, [])
    ...
```

**`backend/config/settings/base.py:136–140`** — cache defaults to `LocMemCache`:

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}
```

**`backend/config/settings/production.py:37–41`** — Channels layer uses Redis, but cache is never overridden.

### Plan

**Option A (preferred, more robust):** Override the cache backend in `production.py` to use Redis:

```python
# backend/config/settings/production.py
if "REDIS_URL" in os.environ:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,  # noqa: F405
        },
    }
```

**Option B (minimal, documented limitation):** Keep LocMemCache but document the limitation in the rate limiter's docstring and in the production settings.

Given the scope (medium severity), **Option B** is proportionate — rate limiting is a defense-in-depth measure, not a primary security control. But document clearly.

Also fix `_should_skip()` to use Django settings instead of `os.environ`:

```python
from django.conf import settings

def _should_skip() -> bool:
    return getattr(settings, "SKIP_RATE_LIMIT", False)
```

And add `SKIP_RATE_LIMIT` to `base.py` env vars.

### Files to change

- `backend/apps/auth/rate_limit.py`
- `backend/config/settings/base.py` (add `SKIP_RATE_LIMIT` env var)
- `backend/config/settings/production.py` (optionally add Redis cache override)
- `docs/adrs/ADR-010-production-hardening.md` (document cache limitation)

---

## AC-7: AUTH_REQUIRED bypass in production

### Current code

**`backend/config/settings/production.py`** — no guardrail for `AUTH_REQUIRED`:

```python
# Guards exist for DATABASE_URL and SECRET_KEY, but NOT for AUTH_REQUIRED
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required in production")
if _insecure_key == SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY must be set to a unique value in production")
```

**`backend/config/settings/base.py:22`**:
```python
AUTH_REQUIRED=(bool, True),
```

**`.env.example:32`**:
```env
AUTH_REQUIRED=True
```

### Plan

1. **`backend/config/settings/production.py`** — Add a startup guardrail:

```python
if not getattr(globals().get("AUTH_REQUIRED", None), None):
    raise RuntimeError(
        "AUTH_REQUIRED must be True in production. "
        "Set AUTH_REQUIRED=True in your environment."
    )
```

Wait — `AUTH_REQUIRED` is loaded via `env()` in `base.py` and is available as `settings.AUTH_REQUIRED` after `from .base import *`. So we can check it at module level:

```python
from django.conf import settings

# After base imports...
if not settings.AUTH_REQUIRED:
    raise RuntimeError("AUTH_REQUIRED must be True in production")
```

But `settings` may not be configured at import time in production.py (Django loads settings lazily). Safer approach: use a `django.setup()`-compatible check, or simply override:

```python
AUTH_REQUIRED = True  # Force it in production regardless of env
```

This is the simplest and most robust approach — override the value in production.py so the env var `AUTH_REQUIRED` is ignored in production:

```python
# backend/config/settings/production.py
AUTH_REQUIRED = True
```

No need for a RuntimeError — just hardcode it to True in production settings. The env var only affects development.py.

2. **`.env.example:32`** — Add a warning comment:
```env
AUTH_REQUIRED=True
# WARNING: This only affects development. Production always enables auth.
```

3. **`backend/config/settings/development.py`** — Optionally (low priority) explicitly set `AUTH_REQUIRED = env.bool("AUTH_REQUIRED", default=True)` to make the intent clear.

### Files to change

- `backend/config/settings/production.py` — hardcode `AUTH_REQUIRED = True`
- `.env.example` — add warning comment

---

## Files changed summary

| File | Change type | Issue |
|---|---|---|
| `frontend/src/pages/CampaignDetail.tsx` | Add try-catch to 6 async handlers | AC-1 |
| `frontend/src/components/ErrorBoundary.tsx` | Gate console.error behind DEV | AC-2 |
| `frontend/src/services/websocket.ts` | Gate console.warn behind DEV + add send() method | AC-3, AC-4 |
| `backend/apps/ai/providers/openai_provider.py` | Narrow except Exception to specific SDK types | AC-5 |
| `backend/apps/ai/providers/anthropic_provider.py` | Narrow except Exception to specific SDK types | AC-5 |
| `backend/apps/auth/rate_limit.py` | Fix _should_skip() to use settings + document LocMemCache limit | AC-6 |
| `backend/config/settings/base.py` | Add SKIP_RATE_LIMIT env var | AC-6 |
| `backend/config/settings/production.py` | Hardcode AUTH_REQUIRED = True | AC-7 |
| `.env.example` | Add AUTH_REQUIRED warning comment | AC-7 |

## Verification

Each check must pass before marking done:

```bash
# Backend
ruff check backend/
mypy backend/
cd backend && uv run pytest

# Frontend
cd frontend && pnpm vitest run
pnpm tsc
pnpm biome check --write .

# All must pass with 0 errors
```
