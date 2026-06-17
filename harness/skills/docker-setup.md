# Skill: Docker Setup

## Purpose
Learn how to write Dockerfiles and Docker Compose configuration for the ACME Content Workflow project.

## When to Use
- When creating or modifying `backend/Dockerfile`
- When creating or modifying `frontend/Dockerfile`
- When creating or modifying root `compose.yml`
- When setting up PostgreSQL, Redis, or other services

## Steps

### 1. Backend Dockerfile
- Use multi-stage builds (builder + production)
- Builder stage: full SDK, install dependencies, run build
- Production stage: distroless or slim image, copy artifacts only
- Run as non-root user (`USER node` or `USER 1001`)
- Example health check: `curl -f http://localhost:3000/health`

### 2. Frontend Dockerfile
- Builder stage: Node image, install deps, build static assets
- Production stage: nginx:alpine, copy build output to `/usr/share/nginx/html`
- Use custom nginx.conf for SPA routing (try_files $uri /index.html)
- Run as non-root nginx user

### 3. Docker Compose (compose.yml)
- Services: `db` (postgres:16-alpine), `backend`, `frontend`
- `db`: healthcheck with `pg_isready`, volume for data persistence
- `backend`: depends_on with condition: service_healthy
- `frontend`: depends_on backend, environment for API URL
- All services on a shared network
- Ports: 5432 (db), 3000 (backend), 5173 (frontend)

### 4. Environment Variables
- Use `${VARIABLE:-default}` pattern for defaults
- Reference `.env.example` in the compose file
- Never hardcode secrets in compose.yml

## Verification
- `docker compose up --build` starts all services
- `docker compose ps` shows all services as healthy
- Backend responds on localhost:3000/api
- Frontend loads on localhost:5173
- `docker compose down` cleans up without losing volumes
