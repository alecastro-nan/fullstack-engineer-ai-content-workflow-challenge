#!/usr/bin/env bash
set -euo pipefail

echo "=== ACME Challenge — Environment Initialization ==="

# 1. Check prerequisites
command -v node >/dev/null 2>&1 || { echo "Node.js is required"; exit 1; }
command -v pnpm >/dev/null 2>&1 || { echo "pnpm is required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker is required"; exit 1; }

# 2. Install backend dependencies
echo "[backend] Installing dependencies..."
if [ -d "backend" ]; then
  cd backend
  if [ -f "package.json" ]; then
    pnpm install
  elif [ -f "requirements.txt" ]; then
    python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
  elif [ -f "go.mod" ]; then
    go mod download
  fi
  cd ..
fi

# 3. Install frontend dependencies
echo "[frontend] Installing dependencies..."
if [ -d "frontend" ]; then
  cd frontend
  pnpm install
  cd ..
fi

# 4. Create .env from example if not exists
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  cp .env.example .env
  echo "Created .env from .env.example — edit with your API keys"
fi

# 5. Start infrastructure (PostgreSQL)
echo "[infra] Starting Docker services..."
docker compose up -d db 2>/dev/null || docker compose up -d
echo "Waiting for PostgreSQL to be ready..."
sleep 3

# 6. Run database migrations
echo "[db] Running migrations..."
if [ -d "backend" ]; then
  cd backend
  if [ -f "package.json" ]; then
    npx prisma migrate dev --name init 2>/dev/null || npx typeorm migration:run 2>/dev/null || true
  elif [ -f "requirements.txt" ]; then
    python -m alembic upgrade head 2>/dev/null || true
  fi
  cd ..
fi

# 7. Verify
echo "=== Environment ready ==="
echo "  Backend  → http://localhost:3000"
echo "  Frontend → http://localhost:5173"
echo "  DB       → postgresql://postgres:postgres@localhost:5432/acme"
echo ""
echo "Run 'docker compose up' to start all services."
