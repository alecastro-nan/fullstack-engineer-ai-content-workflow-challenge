#!/usr/bin/env bash
set -euo pipefail

echo "=== ACME Challenge — Environment Initialization ==="

# 1. Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "Python >=3.12 is required"; exit 1; }
command -v uv >/dev/null 2>&1 || { echo "uv is required (pip install uv)"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js >=18 is required"; exit 1; }
command -v pnpm >/dev/null 2>&1 || { echo "pnpm is required (corepack enable && corepack prepare pnpm@latest --activate)"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker is required"; exit 1; }

# 2. Install backend dependencies
echo "[backend] Installing dependencies..."
cd backend
uv venv .venv
source .venv/bin/activate
uv sync --all-extras
cd ..

# 3. Install frontend dependencies
echo "[frontend] Installing dependencies..."
cd frontend
pnpm install
cd ..

# 4. Create .env from example if not exists
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "Created .env from .env.example — edit with your API keys"
fi

# 5. Start infrastructure (PostgreSQL)
echo "[infra] Starting Docker services..."
docker compose up -d db
echo "Waiting for PostgreSQL to be ready..."
sleep 3

# 6. Run database migrations
echo "[db] Running migrations..."
source backend/.venv/bin/activate
cd backend && python manage.py migrate
cd ..

# 7. Verify
echo "=== Environment ready ==="
echo "  Backend  → http://localhost:8000"
echo "  GraphQL  → http://localhost:8000/graphql"
echo "  Frontend → http://localhost:5173"
echo "  DB       → postgresql://postgres:postgres@localhost:5432/acme"
echo ""
echo "Run 'docker compose up' to start all services."
