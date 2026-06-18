# Security Review — F-002 Install Django Stack

**Reviewer:** @security-reviewer  
**Date:** 2025-06-18  
**Scope:** Backend Django implementation (campaigns, content, AI apps), Docker setup, environment config  
**Gate reference:** AGENTS.md R-007, R-012, R-014  

---

## Summary

| Category | Status |
|---|---|
| Hardcoded secrets | ❌ **1 Critical, 1 High** |
| Security headers | ❌ **Missing critical production settings** |
| Production hardening | ❌ **Partial — gaps in enforcement** |
| Docker security | ⚠️ **Non-root user ✓, but secrets in compose ✗** |
| Secret exposure risk | ⚠️ **Env var defaults could lead to accidental exposure** |
| Model injection | ✅ **Clean, no injection vectors found** |
| Input validation | ✅ **Standard Django/Strawberry practices** |
| **Overall** | **❌ FAIL — 2 critical, 3 high findings that block production readiness** |

---

## 🚨 Critical (Fix Immediately)

### C-001: Hardcoded DJANGO_SECRET_KEY in compose.yml

**File:** `compose.yml` (line 25)  
**Severity:** 🚨 Critical  
**Rule:** R-007 — No hardcoded secrets

```yaml
environment:
  DJANGO_SECRET_KEY: insecure-dev-key-not-for-production
```

The Django secret key is hardcoded in plaintext in `compose.yml`. Every developer running `docker compose up` uses the same weak key. An attacker who knows this key can:

- Forge session cookies and hijack any user session  
- Generate forged CSRF tokens  
- Decrypt any data signed with the key  
- Execute arbitrary code if PickleSerializer is in use (default in older Django)

**Fix:** Use a `.env` file reference instead:

```yaml
env_file:
  - .env
```

Remove `DJANGO_SECRET_KEY` from `compose.yml` entirely. The `.env` file is already in `.gitignore`.

---

### C-002: Hardcoded PostgreSQL Password in compose.yml

**File:** `compose.yml` (lines 5-7)  
**Severity:** 🚨 Critical  
**Rule:** R-007 — No hardcoded secrets

```yaml
environment:
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
```

The database superuser password is hardcoded as `postgres` in the compose file. Combined with port `5432` being exposed to the host, this creates a trivial attack vector if the host is network-accessible.

**Fix:** Same as C-001 — use `env_file` or Docker secrets. Move `POSTGRES_PASSWORD` to `.env`:

```yaml
env_file:
  - .env
```

And reference in compose:

```yaml
environment:
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

---

## ⚠️ High (Fix Before Deployment)

### H-001: Insecure SECRET_KEY Default in base.py

**File:** `backend/config/settings/base.py` (line 23)  
**Severity:** ⚠️ High  
**Rule:** R-007 — No hardcoded secrets (even as defaults)

```python
SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-dev-key-not-for-production")
```

The fallback default `"insecure-dev-key-not-for-production"` is used if `DJANGO_SECRET_KEY` is not set. Critically, **`production.py` does not guard against this fallback** — unlike the DATABASE_URL guard on line 5-6:

```python
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required in production")
```

There is no equivalent:

```python
if SECRET_KEY == "insecure-dev-key-not-for-production":
    raise RuntimeError("DJANGO_SECRET_KEY must be changed in production")
```

**Fix:** Add a guard in `production.py`:

```python
if SECRET_KEY == "insecure-dev-key-not-for-production":
    raise RuntimeError("DJANGO_SECRET_KEY environment variable must be set to a unique, unpredictable value in production")
```

---

### H-002: Missing Production Security Headers

**File:** `backend/config/settings/production.py`  
**Severity:** ⚠️ High

The production settings are missing several critical Django security settings that protect against common web attacks:

| Setting | Status | Risk |
|---|---|---|
| `SECURE_HSTS_SECONDS` | ❌ Missing | No HTTP Strict Transport Security — man-in-the-middle downgrade attacks possible |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | ❌ Missing | Subdomains not covered by HSTS |
| `SECURE_HSTS_PRELOAD` | ❌ Missing | Cannot preload HSTS in browsers |
| `SECURE_SSL_REDIRECT` | ❌ Missing | HTTP traffic not redirected to HTTPS |
| `SECURE_BROWSER_XSS_FILTER` | ❌ Missing | XSS filter not enabled (Django 5.1 deprecates this, but CSP is not configured instead) |
| `SECURE_CONTENT_TYPE_NOSNIFF` | ❌ Missing | MIME-sniffing not disabled |
| `CSRF_TRUSTED_ORIGINS` | ❌ Missing | Cross-origin CSRF protection not configured for GraphQL |
| `CSRF_COOKIE_HTTPONLY` | ❌ Missing | CSRF token accessible via JavaScript |
| `SESSION_COOKIE_HTTPONLY` | ❌ Missing | Session cookie accessible via JavaScript |
| `SESSION_COOKIE_SAMESITE` | ❌ Missing | No SameSite attribute on session cookies |

**Fix:** Add to `production.py`:

```python
# HTTPS / HSTS
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Content security
SECURE_CONTENT_TYPE_NOSNIFF = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# CORS/CSRF
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
```

---

### H-003: DEBUG=True in compose.yml and Default ALLOWED_HOSTS Wildcard

**File:** `compose.yml` (line 26), `base.py` (line 13)  
**Severity:** ⚠️ High  
**Rule:** R-007 — DEBUG can leak sensitive data

```yaml
# compose.yml
DEBUG: "True"
```

```python
# base.py
ALLOWED_HOSTS=(list, ["*"]),
```

Two issues:

1. **`DEBUG=True` in compose.yml** is acceptable for local development but dangerous if the compose file is reused in staging/production-like environments. DEBUG mode leaks stack traces, environment variables (including API keys), database queries, and configuration details on error pages.

2. **`ALLOWED_HOSTS` defaults to `["*"]`** in `base.py`. While `production.py` sets `ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")`, the compose file doesn't set this env var, so the wildcard default from base.py applies. This makes host header injection possible.

**Fix:** 
- Document in compose.yml that DEBUG must be `False` for non-development environments  
- Set `ALLOWED_HOSTS` explicitly in compose.yml for development, e.g. `ALLOWED_HOSTS=localhost,127.0.0.1`  
- Remove the wildcard default in `base.py` or enforce that production.py raises if `*` is used

---

## 📋 Medium (Fix in Next Sprint)

### M-001: CSRF_TRUSTED_ORIGINS Not Configured for GraphQL

**File:** `backend/config/settings/production.py`  
**Severity:** 📋 Medium

The GraphQL endpoint at `/graphql` accepts cross-origin POST requests. Strawberry's GraphQLView handles CSRF by default (requires CSRF token), but without `CSRF_TRUSTED_ORIGINS` set in production, the frontend at the configured `FRONTEND_URL` cannot make authenticated requests without errors.

**Fix:** Add to `production.py`:

```python
CSRF_TRUSTED_ORIGINS = [env("FRONTEND_URL")]
```

---

### M-002: ASGI and manage.py Default to Development Settings

**Files:** `backend/config/asgi.py` (line 5), `backend/manage.py` (line 7)  
**Severity:** 📋 Medium

```python
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
```

Both files use `setdefault()`, meaning if the environment variable is not explicitly set, they default to development settings. If the production Docker container ever starts without `DJANGO_SETTINGS_MODULE` properly set, it could accidentally run with development settings (DEBUG=True, SQLite backend, wildcard ALLOWED_HOSTS).

The Dockerfile does set `DJANGO_SETTINGS_MODULE=config.settings.production` via `ENV`, but `setdefault()` won't override an existing env var so this is fine for the Docker case. However, **human error** (e.g., forgetting to set the env var when running with gunicorn directly) would silently fall back to development settings.

**Fix:** In production.py (or a separate entrypoint script), validate that `DJANGO_SETTINGS_MODULE` points to the production settings explicitly. Alternatively, use `os.environ["DJANGO_SETTINGS_MODULE"]` instead of `setdefault` in the ASGI entrypoint and make the caller responsible.

---

### M-003: Django Admin Exposed Without IP Restriction

**File:** `backend/config/urls.py` (line 8)  
**Severity:** 📋 Medium

```python
path("admin/", admin.site.urls),
```

The Django admin interface is exposed at `/admin/` without any IP whitelisting, rate limiting, or brute-force protection. While Django's admin has built-in login CSRF protection, it remains a high-value target for credential stuffing attacks.

**Fix:** Consider:
- Restricting `/admin/` to internal IPs via a middleware or nginx rule
- Adding rate limiting middleware
- Using a non-standard admin URL prefix in production

---

### M-004: SECURE_PROXY_SSL_HEADER Not Configured

**File:** `backend/config/settings/`  
**Severity:** 📋 Medium

In production behind a reverse proxy (nginx, Traefik, Cloudflare), without `SECURE_PROXY_SSL_HEADER`, Django cannot reliably determine if the request is HTTPS. This breaks `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, and `CSRF_COOKIE_SECURE` — those settings may cause redirect loops or block legitimate requests.

**Fix:** Add to `production.py`:

```python
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```

---

## ℹ️ Low / Info

### I-001: .env.example Contains Default PostgreSQL Credentials

**File:** `.env.example` (line 2)  
**Severity:** ℹ️ Low

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/acme
```

The example file contains default PostgreSQL superuser credentials. This is a standard convention for `.env.example` files and is acceptable since the file only contains placeholders. No action required, but consider documenting that these must be changed.

### I-002: SESSION_COOKIE_AGE — Default Django Value (2 weeks)

**File:** `backend/config/settings/base.py`  
**Severity:** ℹ️ Info

Django's default session cookie age is 1209600 seconds (2 weeks). For an admin/content management system, this may be long-lived. Consider a shorter session expiry (e.g., 86400 = 24 hours) for sensitive operations.

### I-003: GraphQL Introspection Enabled

**File:** `backend/config/schema.py`  
**Severity:** ℹ️ Info

The Strawberry GraphQL schema is created without disabling introspection:

```python
schema = strawberry.Schema(query=Query, mutation=Mutation)
```

By default, introspection is enabled. In production, this exposes the full schema to anyone who queries `__schema` — including type names, fields, and descriptions. While this is common for internal APIs, consider disabling introspection in production via:

```python
schema = strawberry.Schema(query=Query, mutation=Mutation, allow_introspection=False)
```

---

## Pass/Fail by Security Gate (AGENTS.md)

| Gate | Criterion | Result |
|---|---|---|
| R-007 | No hardcoded secrets | ❌ **FAIL** — `compose.yml` hardcodes DJANGO_SECRET_KEY and POSTGRES_PASSWORD |
| R-007 | API keys via env vars | ✅ **PASS** — OPENAI_API_KEY and ANTHROPIC_API_KEY loaded from env only |
| R-014 | No `print()` in production code | ✅ **PASS** — No print() calls found |
| — | Dockerfile runs as non-root | ✅ **PASS** — `USER app` on line 16 |
| — | DEBUG cannot be True in production | ❌ **FAIL** — `production.py` sets DEBUG=False, but `base.py` default and `compose.yml` both set DEBUG=True; no enforcement mechanism |
| — | CSRF protection enabled | ⚠️ **PARTIAL** — `CsrfViewMiddleware` present, but `CSRF_TRUSTED_ORIGINS` not configured |
| — | Security headers applied | ❌ **FAIL** — Multiple critical security headers missing |
| — | .dockerignore excludes secrets | ✅ **PASS** — `.env` and `.git` excluded |
| — | .gitignore excludes .env | ✅ **PASS** — `.env` and `.env.local` in `.gitignore` |
| R-012 | Explicit error handling | ⚠️ **PARTIAL** — Error guards exist for DATABASE_URL but not for SECRET_KEY |

**Total: 4 PASS, 3 FAIL, 2 PARTIAL**

---

## Recommendations Priority Order

1. **IMMEDIATELY** remove hardcoded secrets from `compose.yml` (C-001, C-002)
2. **BEFORE DEPLOYMENT** add SECRET_KEY production guard (H-001)
3. **BEFORE DEPLOYMENT** add missing security headers (H-002)
4. **BEFORE DEPLOYMENT** address DEBUG/ALLOWED_HOSTS for production (H-003)
5. **NEXT SPRINT** implement CSRF_TRUSTED_ORIGINS, admin hardening, proxy header (M-001 through M-004)
6. **BACKLOG** consider introspection disable, session expiry, SSL redirect (I-001 through I-003)
