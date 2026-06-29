# ADR-010: Production Hardening — Infrastructure & Input Validation

## Status
Accepted

## Context
Security audit PR #1 identified 11 infrastructure and configuration hardening items that needed to be addressed to prepare the application for production deployment. These ranged from misconfigured tooling (biome, mypy), to missing security controls (CORS, Content-Type enforcement, XSS sanitization), to production-specific infrastructure (Redis channel layer, database credential handling, admin gating).

## Decision

### 1. Biome scope corrected
Biome is a JS/TS linter only. The `include` field was pointing to a nonexistent `backend/src/` directory. Changed to `["frontend/src"]` only.

### 2. Mypy strict mode with stubs
- Removed `ignore_missing_imports = true` which was hiding real type issues
- Installed `django-stubs` and `channels-stubs` for Django/Channels type awareness
- Configured `mypy_django_plugin.main` plugin for automatic Django model type inference
- Removed `disable_error_code` opting to fix or suppress errors at the source
- Pre-existing issues are suppressed with targeted `# type: ignore[code]` comments

### 3. Admin interface gated behind DEBUG
Django admin exposes sensitive model introspection. In production (`DEBUG=False`), `/admin/` URLs return 404.

### 4. Database credentials handled via individual env vars
Instead of embedding a constructed `DATABASE_URL` with password in `compose.yml`, individual `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` env vars are used. The `settings/base.py` now supports constructing DATABASE_URL from these individual vars as a fallback.

### 5. CORS supports multiple origins
Changed from `CORS_ALLOWED_ORIGINS = [env("FRONTEND_URL")]` (single origin) to `env.list("FRONTEND_URL")` supporting comma-separated origins. Example: `FRONTEND_URL=http://localhost:5173,http://staging.example.com`.

### 6. WebSocket nginx rewrite
The frontend serves WebSocket connections at `/ws/` which nginx proxies to the Django backend. However, Django Channels expects the path without the `/ws` prefix (e.g., `/content/<id>/`). Added `rewrite ^/ws/(.*) /$1 break;` to strip the prefix before proxying.

### 7. Redis channel layer for production
Production `settings/production.py` now configures `CHANNEL_LAYERS` with `channels_redis.core.RedisChannelLayer` using the `REDIS_URL` env var. Development mode continues to use `InMemoryChannelLayer` from `base.py`.

### 8. Content-Type enforcement
POST requests to `/graphql` without `Content-Type: application/json` return 415 Unsupported Media Type. Enforced in `AuthGraphQLView.dispatch()`.

### 9. XSS sanitization
All user-provided text content (`headline`, `description`, `body`) in campaign and content piece services is escaped via `django.utils.html.escape` before storage. This prevents stored XSS attacks via the admin or GraphQL API.

## Consequences
### Positive
- Production-ready security posture for CSRF, XSS, and credential handling
- Mypy now catches real type issues with Django model fields and Channels types
- Explicit configuration surface for production deployment (Redis, JWT, CORS origins)
- Backward compatible — all 172 tests pass and all existing workflows unchanged

### Negative
- Requires Redis for production WebSocket functionality (`InMemoryChannelLayer` suffices for dev)
- Some django-stubs type conflicts required `# type: ignore` suppression (ModelAdmin generics, urlpatterns)
- Production deployment requires explicit `REDIS_URL` and `JWT_SIGNING_KEY` env vars

## Alternatives Considered
- **bleach.clean()** for XSS: Simpler to use `django.utils.html.escape` (zero dependencies) vs adding `bleach` when we only need HTML entity escaping
- **Middleware for Content-Type**: Overriding `dispatch()` in the view is cleaner than a full middleware for a single endpoint
- **Docker secrets** for DB password: Simpler to use env vars for local dev; secrets can be added later for production

## References
- ADR-007: Authentication & access control
- ADR-008: Security controls (GraphQL depth limits, CSP, prompt injection)
