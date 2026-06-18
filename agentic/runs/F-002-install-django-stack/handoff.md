# Handoff — F-002: Install Django + Strawberry GraphQL + Python backend stack

## Meta
- **From:** Builder (Agentic)
- **To:** Code Reviewer
- **Date:** 2026-06-18

## What was done
- `backend/pyproject.toml` with all dependencies: Django 5.2, Strawberry GraphQL, uvicorn, gunicorn, django-environ, channels, daphne, openai, anthropic, psycopg2-binary, pytest, mypy, ruff, django-stubs
- `backend/manage.py` — Django management entrypoint
- `backend/config/` — Django project configuration:
  - `settings/base.py` — shared settings (DATABASES via env, INSTALLED_APPS, STRAWBERRY, CHANNEL_LAYERS, AI provider config)
  - `settings/development.py` — DEBUG=True, SQLite fallback
  - `settings/production.py` — DEBUG=False, PostgreSQL required
  - `urls.py` — /admin/ + /graphql endpoints
  - `wsgi.py` — WSGI application
  - `asgi.py` — ASGI with Channels ProtocolTypeRouter
  - `schema.py` — Strawberry schema with health + ping
- `backend/apps/campaigns/` — Campaign model (UUID PK, name, description, status, timestamps, soft delete)
- `backend/apps/content/` — ContentPiece model (UUID PK, FK to Campaign, state machine: draft/suggested_by_ai/reviewed/approved/rejected)
- `backend/apps/ai/` — AI app skeleton
- `backend/apps/reviews/` — Reviews app skeleton
- `backend/Dockerfile` — Multi-stage (builder with uv, production with gunicorn+uvicorn, non-root user)
- `backend/.dockerignore`
- `compose.yml` — Uncommented Django backend service with depends_on db healthcheck
- `.env.example` — Updated with Django vars (replaced NestJS vars)
- `agentic/knowledge/decisions/005-human-decisions.md` — Recorded all human decisions

## Verification results
- `python manage.py check` — ✅ Passed
- `ruff check .` — ✅ All checks passed
- `mypy .` — ✅ No errors (with django-stubs, disable var-annotated/type-arg)
- `uv sync` — ✅ 57 packages installed cleanly
- `GraphQL introspection` — ✅ Schema valid
- `pytest` — ✅ 2 tests (health/ping queries) passed
- `python manage.py showmigrations` — ✅ Built-in Django apps registered

## Human decisions recorded
| Decision | Choice |
|---|---|
| AI Provider | OpenAI + Anthropic (both) |
| React Framework | Vite |
| Real-time | Django Channels (WebSockets) |
| Delete Strategy | Soft delete |
| AI Generation | Synchronous |
| State Management | Zustand |
| Styling | Tailwind CSS |

## Not done / known issues
- No database migrations applied yet (will be done in F-005)
- No proper SECRET_KEY handling for production (needs env setup)
- Docker compose CLI not available on host machine for `docker compose config` validation

## Next actions
1. @code-reviewer: Review backend/ structure, settings, models, Dockerfile
2. @security-reviewer: Verify no secrets exposed, env var handling
3. After approval: Proceed to F-003 (Campaign CRUD GraphQL API)

## Artifacts
- Decision: `agentic/knowledge/decisions/005-human-decisions.md`
- Migration: Not yet created (will be in F-005)
