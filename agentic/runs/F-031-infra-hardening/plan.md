# Plan — F-031: Infrastructure & Config Hardening

## Meta
- **Task ID:** F-031
- **Branch:** `feat/F-031-infra-hardening`
- **Dependencies:** None
- **Est. time:** ~1h
- **Reviewers:** @code-reviewer, @security-reviewer

## Overview

Address 11 infrastructure and input validation issues from the PR #1 audit. All changes are independent and can be done in any order. Most are single-line or small config edits.

---

## Work Items

### 1. Fix biome.json include (C-8)
**File:** `biome.json`
- Change `"include": ["backend/src", "frontend/src"]` → `"include": ["frontend/src"]`
- Biome is a JS/TS linter; `backend/src` doesn't exist and wouldn't apply to Python

### 2. Fix mypy config (C-9)
**File:** `backend/pyproject.toml`
- Remove `ignore_missing_imports = true`
- Install: `uv add --dev django-stubs channels-stubs`
- Configure plugins:
  ```toml
  [tool.mypy]
  python_version = "3.12"
  strict = true
  exclude = ["migrations", ".venv"]
  plugins = ["mypy_django_plugin"]

  [tool.django-stubs]
  django_settings_module = "config.settings.development"
  ```
- Remove `disable_error_code = ["var-annotated", "type-arg"]` — these should be fixed properly, not silenced

### 3. Gate Django admin behind DEBUG (H-4)
**File:** `backend/config/urls.py`
```python
from django.conf import settings

urlpatterns = []
if settings.DEBUG:
    urlpatterns.append(path("admin/", admin.site.urls))
urlpatterns += [
    path("graphql", csrf_exempt(AuthGraphQLView.as_view(schema=schema))),
    path("", include("apps.ws.routing")),
]
```

### 4. Secure database credentials (H-7)
**File:** `compose.yml`
- Remove inline password from `DATABASE_URL`
- Use individual env vars instead:
  ```yaml
  environment:
    DB_HOST: db
    DB_PORT: "5432"
    DB_NAME: ${POSTGRES_DB:-acme}
    DB_USER: ${POSTGRES_USER:-postgres}
    DB_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
  ```
- Or use Docker secrets for the password
- Update `backend/config/settings/base.py` to support building DATABASE_URL from individual vars

### 5. CORS multi-origin support (H-9)
**File:** `backend/config/settings/base.py`
- Change: `CORS_ALLOWED_ORIGINS = [env("FRONTEND_URL")]` → `CORS_ALLOWED_ORIGINS = env.list("FRONTEND_URL", default=["http://localhost:5173"])`
- Update `.env.example` to show comma-separated example: `FRONTEND_URL=http://localhost:5173,http://staging.example.com`

### 6. nginx WS rewrite (H-10)
**File:** `frontend/nginx.conf`
- Add rewrite rule before proxy_pass:
  ```nginx
  location /ws {
      rewrite ^/ws/(.*) /$1 break;
      proxy_pass http://backend;
      ...
  }
  ```
- This strips `/ws` prefix so Django routes (`ws/content/{id}/`) match correctly

### 7. Fix production.py wildcard import (H-11)
**File:** `backend/config/settings/production.py`
- Add: `from config.settings.base import env`
- Keep the `from .base import *` but now `env` is explicitly imported, removing the fragile implicit dependency

### 8. Redis channel layer for production (H-12)
**File:** `backend/config/settings/production.py`
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [env("REDIS_URL", default="redis://localhost:6379")]},
    },
}
```
- Add `channels-redis` to pyproject.toml: `uv add channels-redis`

### 9. Clean ALLOWED_HOSTS (M-13)
**File:** `backend/config/settings/base.py`
- Remove `"0.0.0.0"` from default: `ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"])`

### 10. Content-Type enforcement (H-5)
**File:** `backend/config/urls.py` or a new middleware
- Add middleware that checks `Content-Type: application/json` on POST to `/graphql`
- Return 415 Unsupported Media Type if Content-Type is not JSON

**Option A (simpler):** Override `parse_body` in `AuthGraphQLView`
**Option B (cleaner):** Add middleware class

### 11. XSS sanitization (H-6)
**File:** `backend/apps/content/services.py` and `backend/apps/campaigns/services.py`
- Import `django.utils.html.escape` or use `bleach.clean()`
- Sanitize headline, description, body on create and update:
  ```python
  from django.utils.html import escape
  headline = escape(validated_data.get("headline", ""))
  ```
- Add `bleach` to dependencies if using it (`uv add bleach`)

---

## Files Changed (complete list)

| File | Change |
|---|---|
| `biome.json` | Fix include path |
| `backend/pyproject.toml` | mypy stubs, plugins, channels-redis |
| `backend/config/urls.py` | Admin gating, Content-Type middleware |
| `backend/config/settings/base.py` | CORS multi-origin, ALLOWED_HOSTS cleanup |
| `backend/config/settings/production.py` | Explicit env import, Redis channel layer |
| `compose.yml` | DB credentials (no inline password) |
| `frontend/nginx.conf` | WS rewrite rule |
| `.env.example` | CORS multi-origin example, REDIS_URL |

---

## Testing Strategy

| Item | Test approach | Key assertions |
|---|---|---|
| 1 | `biome check frontend/src` | Exit code 0, no errors |
| 2 | `mypy backend/` | Catches missing stubs (no false passes) |
| 3 | curl /admin/ when DEBUG=False | 404 NOT FOUND |
| 4 | docker compose config | No password in output |
| 5 | CORS preflight with multiple origins | Proper Vary: Origin header |
| 6 | WebSocket via nginx | Upgrade succeeds (101) |
| 7 | `python manage.py check` | No import errors |
| 8 | `from channels_redis.core import RedisChannelLayer` | Import succeeds |
| 10 | POST /graphql with text/plain | 415 UNSUPPORTED MEDIA TYPE |
| 11 | Content with `<script>alert(1)</script>` | Stored as escaped entities |

## Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| mypy stubs require code changes to pass | Medium | Run mypy after adding stubs; fix any new errors as they appear |
| Redis channel layer makes compose.yml more complex | Low | Keep InMemoryChannelLayer as dev default, Redis only in production.py |
| Content-Type enforcement breaks existing GraphQL clients | Low | GraphQL playground sends JSON by default; document in README |
