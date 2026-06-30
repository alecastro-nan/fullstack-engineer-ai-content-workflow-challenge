# Handoff — F-034: Fix critical issues from consolidated PR review

## Meta

| Field | Value |
|---|---|
| **From** | @builder |
| **To** | @code-reviewer, @security-reviewer, @database-reviewer |
| **Date** | 2026-06-29 19:16 UTC |

## What was done

### CRIT-1: JWT signing key separation from SECRET_KEY
- `backend/apps/auth/services.py:17-18` — `_get_jwt_secret()` now raises `RuntimeError` if `JWT_SIGNING_KEY` is not configured (no fallback to `SECRET_KEY`)
- `backend/config/settings/production.py:14-17` — validates `JWT_SIGNING_KEY` is set at startup using `env("JWT_SIGNING_KEY")`
- `.env.example:33` — `JWT_SIGNING_KEY` uncommented with production warning
- `backend/conftest.py:11-14` — added `autouse` pytest fixture providing `override_settings(JWT_SIGNING_KEY="test-jwt-key-not-for-production")` so all existing tests pass without individual overrides
- `agentic/knowledge/decisions/008-jwt-key-separation.md` — decision note created

### CRIT-2: CSRF bypass on GraphQL endpoint
- `backend/config/settings/base.py:32` — `CORS_ALLOW_CREDENTIALS = False` (no cookie-based auth used)
- `backend/config/urls.py:14-17` — added safety comment explaining why `csrf_exempt` is safe for JSON-only Bearer token auth

### CRIT-3: Soft-delete cascade from campaigns to content pieces
- `backend/apps/campaigns/services.py:78-87` — `soft_delete_campaign` now cascades `is_deleted=True` and `deleted_at` to all `campaign.content_pieces` via `.update()`
- `docs/adrs/ADR-004-database-schema.md` — updated FK behavior section from CASCADE to PROTECT + application-level cascade; added `deletedAt` to both table schemas

### CRIT-4: Missing `deleted_at` on Campaign model
- `backend/apps/campaigns/models.py:30` — added `deleted_at = models.DateTimeField(null=True, blank=True, editable=False)`
- `backend/apps/campaigns/migrations/0003_add_deleted_at_to_campaign.py` — new migration
- `backend/apps/campaigns/services.py:78-87` — sets `deleted_at = timezone.now()` on soft delete

## Verification results

| Check | Status |
|---|---|
| `ruff check .` | 0 errors |
| `mypy .` | 0 errors |
| `pytest` | 172/172 passed |
| Migration check | up to date |

## Files changed

| File | Change |
|---|---|
| `backend/apps/auth/services.py` | `_get_jwt_secret()` raises RuntimeError |
| `backend/config/settings/production.py` | JWT_SIGNING_KEY validation via env() |
| `.env.example` | JWT_SIGNING_KEY uncommented |
| `backend/conftest.py` | Added autouse JWT_SIGNING_KEY fixture |
| `backend/config/settings/base.py` | CORS_ALLOW_CREDENTIALS = False |
| `backend/config/urls.py` | csrf_exempt safety comment |
| `backend/apps/campaigns/services.py` | Cascade + deleted_at in soft_delete |
| `backend/apps/campaigns/models.py` | deleted_at field added |
| `backend/apps/campaigns/migrations/0003_add_deleted_at_to_campaign.py` | New migration |
| `docs/adrs/ADR-004-database-schema.md` | Updated FK behavior + deletedAt |
| `agentic/knowledge/decisions/008-jwt-key-separation.md` | New decision note |

## Next actions
1. @code-reviewer: verify all 4 critical issues are properly addressed
2. @security-reviewer: confirm CRIT-1 and CRIT-2 resolved
3. @database-reviewer: confirm CRIT-3 and CRIT-4 resolved