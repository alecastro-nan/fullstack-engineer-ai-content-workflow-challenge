# Handoff — F-035: Address 7 remaining medium/major code quality issues

## Meta
- **From:** Builder
- **To:** Code Reviewer
- **Date:** 2025-01-01

## What was done

### AC-1 (Major) — Unhandled promise rejections in CampaignDetail
- Added try-catch to all 6 async handlers: handleCreate, handleUpdate, handleGenerateDraft, handleReview, handleTranslate, handleEditContent
- Each catch sets a user-facing error message via `setError()`
- File: `frontend/src/pages/CampaignDetail.tsx`

### AC-2 — console.error in ErrorBoundary
- Gated `console.error` behind `import.meta.env.DEV`
- File: `frontend/src/components/ErrorBoundary.tsx`

### AC-3 — console.warn in websocket.ts
- Gated `console.warn` behind `import.meta.env.DEV`
- File: `frontend/src/services/websocket.ts`

### AC-4 — Missing WebSocket send() method
- Added public `send(contentId, data)` method to `WebSocketService`
- Returns silently (with DEV-only warning) if connection is not OPEN
- File: `frontend/src/services/websocket.ts`

### AC-5 — Broad except Exception in AI providers
- OpenAI provider: catches `openai.APIError` instead of `Exception`; rate limit string detection within APIError handler
- Anthropic provider: catches `anthropic.APIError` instead of `Exception`; same pattern
- Added `import logging` and `logger.error()` for non-rate-limit API errors
- Updated tests to construct proper `APIError(message, request, body=None)` instances
- Files: `openai_provider.py`, `anthropic_provider.py`, `test_ai_service.py`, `test_anthropic_provider.py`

### AC-6 — Rate limiting _should_skip() uses os.environ + settings
- `_should_skip()` checks `os.environ` first (test compatibility), falls back to Django settings
- Added `SKIP_RATE_LIMIT = env("SKIP_RATE_LIMIT")` to `base.py`
- LocMemCache limitation documented in the rate limiter
- Files: `rate_limit.py`, `config/settings/base.py`

### AC-7 — AUTH_REQUIRED bypass in production
- Hardcoded `AUTH_REQUIRED = True` in `production.py`
- Added warning comment in `.env.example`
- Files: `config/settings/production.py`, `.env.example`

## Documentation updated
- `agentic/runs/F-035-address-quality-issues/plan.md` (implementation notes)

## Not done / known issues
- LocMemCache limitation per AC-6: the rate limiter uses Django's default LocMemCache, which is per-process. Does not work across multiple workers/containers. Option A (Redis cache) was not implemented due to low severity — documented in code.

## Verification
- Backend: 172 tests passed, ruff check clean
- Frontend: 92 tests passed, `tsc --noEmit` clean
- Biome lint has pre-existing warnings (a11y, style) not related to this task

## Next actions
1. Code Reviewer: review all changed files, verify error handling correctness
2. Security Reviewer: confirm no secrets exposure, verify AUTH_REQUIRED guard

## Artifacts
- Commit: `a1231d0` on `feat/F-035-address-quality-issues`
