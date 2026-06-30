# Handoff — F-031: Infrastructure & Config Hardening

## Meta
- **From:** Builder
- **To:** Code Reviewer, Security Reviewer
- **Date:** 2025-01-01

## What was done

### Infrastructure & Config
- **biome.json**: Fixed `include` path — removed nonexistent `backend/src`, now only `["frontend/src"]` (C-8)
- **mypy config**: Removed `ignore_missing_imports = true`, installed `django-stubs` + `channels-stubs`, configured `mypy_django_plugin.main` plugin, removed `disable_error_code` (C-9)
- **Admin gating**: `/admin/` URLs included only when `DEBUG=True` (H-4)
- **DB credentials**: `compose.yml` uses individual `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD` env vars instead of inline `DATABASE_URL` (H-7)
- **base.py**: Supports building `DATABASE_URL` from individual `DB_*` env vars as fallback when `DATABASE_URL` is not set
- **CORS**: Changed from single-string `env("FRONTEND_URL")` to `env.list("FRONTEND_URL")` supporting multiple origins (H-9)
- **nginx**: Added `rewrite ^/ws/(.*) /$1 break;` to `/ws/` location block for proper WebSocket proxying (H-10)
- **production.py**: Added explicit `from config.settings.base import env` import; Redis-backed `CHANNEL_LAYERS` via `channels_redis` when `REDIS_URL` is set (H-11, H-12)
- **ALLOWED_HOSTS**: Removed `"0.0.0.0"` from defaults (M-13)
- **channels-redis**: Added as dependency in `pyproject.toml`

### Input Validation & Security
- **Content-Type enforcement**: `AuthGraphQLView.dispatch()` returns 415 for POST requests without `application/json` Content-Type (H-5)
- **XSS sanitization**: `headline`, `description`, `body` in both `campaigns/services.py` and `content/services.py` escaped via `django.utils.html.escape` on create and update (H-6)

### Documentation updated
- `docs/adrs/ADR-010-production-hardening.md`: Created documenting all infra hardening decisions
- `.env.example`: Updated `FRONTEND_URL` to show comma-separated multi-origin format
- `README.md`: Referenced in ADR-010

## Test results
- **pytest**: 172/172 passed
- **ruff**: 0 errors
- **mypy**: 0 errors (strict mode with django-stubs)
- **tsc**: 0 errors
- **pnpm build**: succeeded

## Not done / known issues
- Redis channel layer is only configured in `production.py`; dev mode still uses `InMemoryChannelLayer` per existing base.py config
- Some pre-existing mypy issues fixed with targeted `# type: ignore` comments (ModelAdmin, urlpatterns, channel layer types)

## Next actions
1. Code Reviewer: verify all config changes, mypy plugin setup, XSS sanitization
2. Security Reviewer: verify Content-Type enforcement, XSS escaping, credential handling
