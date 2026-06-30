# Handoff — F-006: Frontend Dockerfile

## Meta
- **From:** Builder
- **To:** Code Reviewer
- **Date:** 2026-06-19

## What was done
- `frontend/Dockerfile` — multi-stage build (node:20-alpine builder + nginx:alpine production)
- `frontend/nginx.conf` — nginx config on port 5173, proxies /graphql → backend:8000 and /ws → backend:8000
- `frontend/.dockerignore` — excludes node_modules, .git, dist, *.md, .env, coverage

## Design decisions
- Nginx serves static assets from `/usr/share/nginx/html` (Vite build output)
- `/` route uses `try_files` to support SPA client-side routing
- `/assets` has 1-year cache header for immutability
- WebSocket upgrade support on both `/graphql` and `/ws` paths
- Non-root `app` user in production stage (R-007 security)
- Port matches compose.yml frontend service port (5173)

## Not done / known issues
- Build could not be verified locally (Docker daemon not available on this machine)

## Next actions
1. Code Reviewer: review Dockerfile, nginx.conf, .dockerignore
2. Security Reviewer: verify non-root user, no secrets in image
3. Run `docker compose up --build` to verify end-to-end (F-007 will do this)

## Artifacts
- `frontend/Dockerfile`
- `frontend/nginx.conf`
- `frontend/.dockerignore`
