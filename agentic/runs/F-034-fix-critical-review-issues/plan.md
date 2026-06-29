# Plan — F-034: Fix critical issues from consolidated PR review

## Meta

| Field | Value |
|---|---|
| **Task ID** | F-034 |
| **Branch** | `feat/F-034-fix-critical-review-issues` |
| **Base** | `feat/agentic-plan` |
| **Author** | @builder |
| **Reviewers** | @code-reviewer, @security-reviewer, @database-reviewer |
| **Est. time** | 45min |

## Overview

Address 4 critical issues found by subagent review of PR #1 (feat/agentic-plan → main). These are blocking issues that must be fixed before the PR can be merged.

### Issues to fix

| ID | Severity | Area | Description |
|---|---|---|---|
| CRIT-1 | Security | JWT signing key | `_get_jwt_secret()` falls back to `settings.SECRET_KEY` whose default is `"insecure-dev-key-not-for-production"`. Attacker can forge arbitrary JWTs. |
| CRIT-2 | Security | CSRF bypass | GraphQL endpoint is `csrf_exempt` with `CORS_ALLOW_CREDENTIALS = True`. |
| CRIT-3 | Database | Soft-delete cascade | `soft_delete_campaign` does not cascade `is_deleted=True` to content pieces — orphans remain visible. |
| CRIT-4 | Database | Missing `deleted_at` | Campaign model has no `deleted_at` timestamp (ContentPiece does). |

---

## CRIT-1: JWT signing key separation

### Current code

**`backend/apps/auth/services.py:17-18`:**
```python
def _get_jwt_secret() -> str:
    return cast(str, getattr(settings, "JWT_SIGNING_KEY", None) or settings.SECRET_KEY)
```

**`backend/config/settings/base.py:23,26`:**
```python
JWT_SIGNING_KEY=(str, ""),
SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-dev-key-not-for-production")
```

**`.env.example:33`:**
```env
# JWT_SIGNING_KEY=separate-key-for-jwt-signing
```

### Plan

1. **`backend/apps/auth/services.py:17-18`** — Replace fallback with explicit error:
   ```python
   def _get_jwt_secret() -> str:
       key = cast(str, getattr(settings, "JWT_SIGNING_KEY", None))
       if not key:
           raise RuntimeError(
               "JWT_SIGNING_KEY is not configured. "
               "It must be set separately from DJANGO_SECRET_KEY in production."
           )
       return key
   ```

2. **`backend/config/settings/production.py`** — Add validation that JWT_SIGNING_KEY is set:
   ```python
   if not getattr(globals().get("JWT_SIGNING_KEY"), None):
       raise RuntimeError("JWT_SIGNING_KEY must be set in production")
   ```

3. **`.env.example:33`** — Uncomment and add warning:
   ```env
   JWT_SIGNING_KEY=your-separate-jwt-signing-key
   # WARNING: In production, JWT_SIGNING_KEY must be set separately from DJANGO_SECRET_KEY
   ```

### Test implications

- Existing auth tests that rely on `settings.SECRET_KEY` as the JWT key will need `@override_settings(JWT_SIGNING_KEY="test-key")`
- New test for `_get_jwt_secret()` raising `RuntimeError` when JWT_SIGNING_KEY is unset

---

## CRIT-2: CSRF bypass on GraphQL endpoint

### Current code

**`backend/config/urls.py:4,14-16`:**
```python
from django.views.decorators.csrf import csrf_exempt

urlpatterns.append(
    path("graphql", csrf_exempt(AuthGraphQLView.as_view(schema=schema))),
)
```

### Context

The endpoint already validates Content-Type in `AuthGraphQLView.dispatch()` (`backend/apps/auth/views.py:15` — rejects non-`application/json` with 415). This is a GraphQL API that only accepts `application/json` POST requests and uses `Authorization: Bearer <token>` headers (not cookies). Django's CSRF protection is designed for cookie-based auth and form-encoded POST — for JSON APIs, the Content-Type check is the correct CSRF mitigation.

However, the current implementation has these issues:
- `csrf_exempt` is too broad — no `X-Requested-With` header check
- `CORS_ALLOW_CREDENTIALS = True` is unnecessary (no cookies used) and expands attack surface

### Plan

1. **`backend/config/settings/base.py:32`** — Set `CORS_ALLOW_CREDENTIALS = False` (no cookie-based auth is used)

2. **`backend/apps/auth/views.py:14-21`** — Add `X-Requested-With` header check alongside the existing Content-Type check:
   ```python
   def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponseBase:
       if request.method == "POST":
           if request.content_type != "application/json":
               return HttpResponse(
                   "Unsupported Media Type. Content-Type must be application/json",
                   status=415,
                   content_type="text/plain",
               )
           if request.headers.get("X-Requested-With") != "XMLHttpRequest":
               return HttpResponse(
                   "Bad Request: X-Requested-With header required",
                   status=400,
                   content_type="text/plain",
               )
       return super().dispatch(request, *args, **kwargs)
   ```

   Wait — `X-Requested-With` is set by default in `XMLHttpRequest` and `fetch` from same-origin, but GraphQL clients like Apollo URQL may not set it. Let me reconsider.

   Better approach: keep `csrf_exempt` for now (the Content-Type validation already prevents CSRF for JSON endpoints), but:
   - Document why `csrf_exempt` is safe here (JSON-only, Bearer token auth, no cookies)
   - Set `CORS_ALLOW_CREDENTIALS = False`

3. **`backend/config/settings/base.py:32`**:
   ```python
   CORS_ALLOW_CREDENTIALS = False
   ```

4. **`backend/config/urls.py:15`** — Add comment explaining the CSRF exemption:
   ```python
   # csrf_exempt is safe here: this is a JSON-only GraphQL endpoint using
   # Bearer token auth (no cookies). Content-Type validation in
   # AuthGraphQLView.dispatch() rejects form-encoded POST requests.
   path("graphql", csrf_exempt(AuthGraphQLView.as_view(schema=schema))),
   ```

### Files to change

- `backend/config/settings/base.py:32` — `CORS_ALLOW_CREDENTIALS = False`
- `backend/config/urls.py:15` — add safety comment

---

## CRIT-3: Soft-delete cascade for campaigns

### Current code

**`backend/apps/campaigns/services.py:82-83`:**
```python
campaign.is_deleted = True
campaign.save(update_fields=["is_deleted", "updated_at"])
```

Only marks the campaign as deleted — does not cascade to content pieces.

### Plan

1. **`backend/apps/campaigns/services.py:82-83`** — Add cascade:
   ```python
   from django.utils import timezone
   
   campaign.is_deleted = True
   campaign.deleted_at = timezone.now()
   campaign.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
   # Cascade soft delete to all content pieces
   campaign.content_pieces.all().update(is_deleted=True, deleted_at=timezone.now())
   ```

2. **`docs/adrs/ADR-004-database-schema.md`** — Update the FK behavior section to reflect current reality: PROTECT at DB level (prevents accidental hard deletes) with application-level cascade for soft deletes.

### Test implications

- Update existing soft-delete tests in `backend/apps/campaigns/tests/` to verify content pieces are also soft-deleted
- New test: fetch content pieces after campaign soft-delete, assert `is_deleted=True`

---

## CRIT-4: Missing `deleted_at` on Campaign model

### Current code

**`backend/apps/campaigns/models.py:29`:**
```python
is_deleted = models.BooleanField(default=False)
```

No `deleted_at` field, unlike ContentPiece which has it (line 37).

### Plan

1. **`backend/apps/campaigns/models.py:29`** — Add after `is_deleted`:
   ```python
   deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
   ```

2. **Migration** — Create `backend/apps/campaigns/migrations/0003_add_deleted_at_to_campaign.py`

3. **`backend/apps/campaigns/services.py:78-84`** — Already updated in CRIT-3 plan above (sets `deleted_at = timezone.now()`)

### Test implications

- Verify `deleted_at` is set on soft delete
- Verify `deleted_at` is `None` when `is_deleted=False`

---

## Files changed summary

| File | Change type | Issue |
|---|---|---|
| `backend/apps/auth/services.py:17-18` | Modify | CRIT-1 |
| `backend/config/settings/production.py` | Add validation | CRIT-1 |
| `.env.example:33` | Uncomment + warn | CRIT-1 |
| `backend/config/settings/base.py:32` | `CORS_ALLOW_CREDENTIALS = False` | CRIT-2 |
| `backend/config/urls.py:15` | Add safety comment | CRIT-2 |
| `backend/apps/campaigns/services.py:78-84` | Add cascade + deleted_at | CRIT-3, CRIT-4 |
| `backend/apps/campaigns/models.py:29` | Add `deleted_at` field | CRIT-4 |
| `backend/apps/campaigns/migrations/0003_add_deleted_at_to_campaign.py` | New migration | CRIT-4 |
| `docs/adrs/ADR-004-database-schema.md` | Update FK behavior | CRIT-3 |

## Verification

```bash
ruff check backend/
mypy backend/
cd backend && uv run pytest
cd frontend && pnpm vitest run
pnpm tsc
```

All must pass with 0 errors and 0 failures.