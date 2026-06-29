# Decision: 2026-06-29 — JWT signing key separation from SECRET_KEY

## Context
Security audit (CRIT-1) found that `_get_jwt_secret()` in `backend/apps/auth/services.py` falls back to `settings.SECRET_KEY` when `JWT_SIGNING_KEY` is not set. The default `SECRET_KEY` is `"insecure-dev-key-not-for-production"`, meaning an attacker who knows this default can forge arbitrary JWT tokens.

## Decision
- `_get_jwt_secret()` raises `RuntimeError` if `JWT_SIGNING_KEY` is not configured — no fallback to `SECRET_KEY`
- `backend/config/settings/production.py` validates `JWT_SIGNING_KEY` is non-empty at startup
- `.env.example` now has `JWT_SIGNING_KEY` uncommented with a production warning

## Rationale
- `SECRET_KEY` and `JWT_SIGNING_KEY` should be separate secrets per security best practices
- Raising an error at startup (fail-fast) is better than silently using an insecure default
- Validation in `production.py` ensures the key is always set in production environments

## References
- CWE-321: Use of Hard-coded Cryptographic Key
- CWE-330: Use of Insufficiently Random Values
- Issue: CRIT-1 in consolidated PR review