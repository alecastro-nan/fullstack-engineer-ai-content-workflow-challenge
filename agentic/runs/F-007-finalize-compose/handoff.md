# Handoff — F-007: Finalize Docker Compose

## Meta
- **From:** Builder
- **To:** Code Reviewer
- **Date:** 2026-06-19

## What was done

### compose.yml
- Added `restart: unless-stopped` to all 3 services (db, backend, frontend)
- Added backend healthcheck using Python's urllib to verify GraphQL endpoint
- Frontend now depends on backend with `condition: service_healthy` (waits for backend readiness)
- Moved `VITE_API_URL` from runtime `environment` to build-time `args` (Vite embeds at build time)
- Frontend build now passes `VITE_API_URL: ""` so axios uses relative URLs through nginx proxy

### frontend/Dockerfile
- Added `ARG VITE_API_URL` with empty string default, passed at build to `pnpm build`
- Added `apk add curl` in production stage for HEALTHCHECK
- HEALTHCHECK uses `curl -f http://localhost:5173/`

### frontend/.env.example
- Fixed port from 3000 to 8000 for `VITE_API_URL` and `VITE_WS_URL`

### Root .env.example
- Added `VITE_API_URL` and `VITE_WS_URL` entries for local dev

### frontend/src/services/api.ts
- Changed fallback from `'/api'` to `''` — nginx proxies `/graphql`, not `/api`

## State before vs after

| Aspect | Before | After |
|---|---|---|
| Backend healthcheck | None | Python urllib on /graphql |
| Frontend depends_on | Container start only | Waits for backend healthy |
| VITE_API_URL | Runtime env (ineffective) | Build arg (works at build) |
| api.ts fallback | `/api` (wrong for nginx) | `''` (relative URLs work) |
| restart policy | None | `unless-stopped` on all |

## Not done / known issues
- Docker daemon not available — could not run `docker compose up --build` to verify
- `docker compose config` should be run to validate YAML syntax

## Next actions
1. Code Reviewer: review compose.yml, Dockerfile, env files, api.ts
2. Security Reviewer: verify no secrets exposed
3. Run `docker compose config` and `docker compose up --build` to verify

## Artifacts
- `compose.yml` — updated with healthchecks, restart, build args
- `frontend/Dockerfile` — added ARG VITE_API_URL + curl for HEALTHCHECK
- `frontend/.env.example` — port fix
- `.env.example` — added frontend vars
- `frontend/src/services/api.ts` — baseURL fallback fix
