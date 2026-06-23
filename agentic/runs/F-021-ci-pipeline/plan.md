# Plan — F-021: GitHub Actions CI

## Analysis

**Current state:** `.github/workflows/ci.yml` is an old NestJS-era pipeline that uses `pnpm` for everything (backend included). Since the backend is now Python/Django, all existing jobs are broken.

**What needs to change:** Full replacement with 5 jobs:
1. `ruff-lint` — ruff check on `backend/`
2. `mypy-typecheck` — mypy strict mode on `backend/`
3. `pytest-backend` — pytest with coverage on `backend/`
4. `vitest-frontend` — vitest on `frontend/`
5. `docker-build` — verify both backend and frontend Docker images build

**Dependency chain:**
- Python jobs (`ruff`, `mypy`, `pytest`) share the same setup (Python 3.12 + uv)
- Frontend job uses Node 22 + pnpm
- Docker job is independent

## Implementation

### CI workflow (`.github/workflows/ci.yml`)
- Trigger: push (main, feat/**) and pull_request (main) — same as before
- Python 3.12 via `actions/setup-python@v5`
- uv install via `astral-sh/setup-uv@v5`
- `uv sync` includes dev dependencies (mypy, ruff, pytest)
- Each Python job is independent with its own `uv sync` step for isolation
- Frontend uses `pnpm/action-setup@v4` + `actions/setup-node@v4` + `pnpm install --frozen-lockfile`
- Docker build uses `docker compose build` to verify both images

### README update
- Add CI status badge: `[![CI](https://github.com/alecastro-nan/fullstack-engineer-ai-content-workflow-challenge/actions/workflows/ci.yml/badge.svg)](https://github.com/alecastro-nan/fullstack-engineer-ai-content-workflow-challenge/actions/workflows/ci.yml)`
- Document CI pipeline in contributing section

## Files modified
- `.github/workflows/ci.yml`: complete rewrite
- `README.md`: add CI badge + pipeline docs
- `agentic/tasks/feature_list.json`: F-021 → done
- `agentic/tasks/session-progress.md`: F-021 → DONE
- `agentic/runs/F-021-ci-pipeline/plan.md`: this file
