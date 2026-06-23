# ACME GLOBAL MEDIA — AI Content Workflow Platform

[![CI](https://github.com/alecastro-nan/fullstack-engineer-ai-content-workflow-challenge/actions/workflows/ci.yml/badge.svg)](https://github.com/alecastro-nan/fullstack-engineer-ai-content-workflow-challenge/actions/workflows/ci.yml)

A campaign content management system with AI-powered drafting, translation/localization, and human-in-the-loop review. Built for the NaN Labs Fullstack Engineer Challenge.

## Tech Stack

| Layer | Technology | Rationale | ADR |
|---|---|---|---|
| **Backend** | Django 5.1 + Strawberry GraphQL | Type-safe GraphQL from Python types, mature ORM, built-in admin | [ADR-005](docs/adrs/ADR-005-django-strawberry-architecture.md) |
| **Frontend** | React 19 + Vite 6 + React Router 7 + Tailwind CSS 4 | Fast HMR, component-based UI, utility-first styling | — |
| **Database** | PostgreSQL 16 | ACID compliance, JSONB for AI metadata, robust migration tooling | [ADR-004](docs/adrs/ADR-004-database-schema.md) |
| **Real-time** | Django Channels (WebSocket) | First-party Django ASGI extension, per-content-piece group broadcasts | [ADR-003](docs/adrs/ADR-003-real-time-mechanism.md) |
| **AI** | OpenAI SDK + Anthropic SDK | Abstracted via `AIProvider` protocol with automatic fallback | [ADR-002](docs/adrs/ADR-002-ai-provider.md) |
| **API** | GraphQL (Strawberry) | Flexible queries, single endpoint, built-in playground | [ADR-001](docs/adrs/ADR-001-rest-vs-graphql.md) |
| **Containers** | Docker + Docker Compose | One-command local stack, reproducible environments | — |
| **Package Mgmt** | uv (Python) / pnpm (JavaScript) | Fast deterministic installs, lockfile-based | — |

## Architecture

```
┌─ Frontend (Vite + React 19) ────────────────────────┐
│  Campaign Dashboard                                  │
│    → Campaign Detail                                 │
│      → Content Piece list + state badges             │
│      → AI Draft Panel (generate + preview)           │
│      → Review UI (approve/reject/edit)               │
│      → Translation Panel (select language + preview) │
└────────────────────┬─────────────────────────────────┘
                     │ GraphQL (HTTP) + WebSocket (WS)
                     ▼
┌─ Backend (Django 5.1 + Strawberry GraphQL) ─────────┐
│  apps/                                               │
│    campaigns/   → Campaign CRUD                      │
│    content/     → ContentPiece CRUD + state machine  │
│    ai/          → AI provider abstraction + dispatch  │
│    reviews/     → Review actions + state history      │
│    ws/          → WebSocket consumer + signal broadcast│
│  ASGI: HTTP /graphql + WS /ws/content/{id}/           │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌─ Infrastructure ────────────────────────────────────┐
│  PostgreSQL 16                                       │
│  Redis (optional, for production channel layer)       │
└──────────────────────────────────────────────────────┘
```

## Features

### Implemented

- **Campaign CRUD** — Create, read, update, soft-delete campaigns via GraphQL
- **ContentPiece CRUD** — Create, read, update, soft-delete content pieces with per-campaign listing
- **AI Draft Generation** — Generate headlines and descriptions from a content brief using OpenAI or Anthropic
- **AI Translation** — Translate content into 7 languages (es, fr, de, pt, it, ja, zh) with automatic copy creation
- **AI Provider Abstraction** — Protocol-based provider layer supporting both OpenAI and Anthropic with automatic fallback on rate limits or failures
- **Review State Machine** — State transitions (DRAFT → SUGGESTED_BY_AI → REVIEWED → APPROVED/REJECTED) with guards, full audit trail via `StateHistory`
- **Real-time WebSocket Broadcasts** — Live state change notifications via Django Channels, per-content-piece groups
- **React Frontend** — Full UI with campaign dashboard, detail pages, AI draft panel, review controls, and translation panel
- **Docker Compose** — One-command `docker compose up --build` runs PostgreSQL, backend, and frontend
- **CI Pipeline** — GitHub Actions: ruff lint, mypy type check, pytest (with coverage), vitest, Docker build check

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | ≥3.12 | Backend runtime |
| Node.js | ≥18 LTS | Frontend runtime |
| uv | ≥0.5.x | Python package manager |
| pnpm | ≥9.x | JavaScript package manager (`corepack enable && corepack prepare pnpm@9 --activate`) |
| Docker | ≥24.x | Containerization |
| Docker Compose | ≥2.24.x | Multi-container orchestration |
| psql | ≥16.x | Direct database inspection |

## How to Run

### Option 1: Docker Compose (full stack, recommended)

```bash
# Edit .env with your API keys first
cp .env.example .env

# Start everything
docker compose up --build
```

This starts PostgreSQL, the Django backend (with Daphne ASGI server), and the frontend (nginx-served static build). Backend runs automatic migrations on startup.

### Option 2: Manual (for development)

```bash
# 1. Prerequisites check
python3 --version    # ≥3.12
node --version       # ≥18
uv --version         # ≥0.5
pnpm --version       # ≥9
docker --version     # ≥24

# 2. Install backend dependencies
cd backend
uv venv .venv
source .venv/bin/activate
uv sync

# 3. Install frontend dependencies
cd ../frontend
pnpm install

# 4. Create .env and configure
cd ..
cp .env.example .env   # edit with your API keys

# 5. Start PostgreSQL
docker compose up -d db

# 6. Run migrations
cd backend
source .venv/bin/activate
python manage.py migrate

# 7. Start backend (in terminal 1)
python manage.py runserver

# 8. Start frontend (in terminal 2)
cd frontend
pnpm dev
```

### Option 3: Automated init script

```bash
./init.sh
```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | `postgresql://postgres:postgres@localhost:5432/acme` | PostgreSQL connection string |
| `DJANGO_SECRET_KEY` | Yes | — | Django secret key for crypto signing |
| `OPENAI_API_KEY` | One of | — | OpenAI API key (for draft/translation generation) |
| `ANTHROPIC_API_KEY` | One of | — | Anthropic API key (fallback provider) |
| `AI_PROVIDER` | No | `openai` | Active AI provider (`openai` or `anthropic`) |
| `DJANGO_SETTINGS_MODULE` | No | `config.settings.development` | Django settings module |
| `DEBUG` | No | `True` | Django debug mode |
| `FRONTEND_URL` | No | `http://localhost:5173` | CORS allowed origin |
| `PORT` | No | `8000` | Backend server port |
| `REDIS_URL` | No | — | Redis connection (optional, for production channel layer) |

## Available Scripts

```bash
# Backend (Python + Django)
cd backend
uv sync                    # Install/update dependencies
python manage.py migrate   # Run database migrations
python manage.py runserver # Start dev server (WSGI)
uv run daphne config.asgi:application  # Start ASGI server (for WebSockets)
uv run ruff check .        # Lint Python code
uv run mypy .             # Type-check Python code with strict mode
uv run pytest --cov       # Run all tests with coverage
uv run pytest --no-header  # Run all tests (terse output)

# Frontend (React + Vite)
cd frontend
pnpm install              # Install/update dependencies
pnpm dev                  # Start Vite dev server
pnpm build                # Production build
pnpm test                 # Run vitest tests
pnpm test:coverage        # Run tests with coverage report
pnpm lint                 # Lint with Biome
pnpm typecheck            # TypeScript type check

# Docker
docker compose up --build # Start full stack
docker compose up -d db   # Start PostgreSQL only
docker compose logs -f    # Follow logs
docker compose down       # Stop all services
```

## GraphQL API

The API is available at `http://localhost:8000/graphql` with an interactive GraphQL playground in development mode.

### Campaigns

```graphql
# Create a campaign
mutation {
  createCampaign(input: { name: "Summer Campaign", description: "Q3 marketing" }) {
    id name description status createdAt updatedAt
  }
}

# List campaigns (paginated)
query {
  campaigns(page: 1, perPage: 20) {
    items { id name description status createdAt }
    totalCount page perPage
  }
}

# Get single campaign
query {
  campaign(id: "uuid-here") { id name description status }
}

# Update campaign
mutation {
  updateCampaign(id: "uuid-here", input: { name: "Updated Name", status: ARCHIVED }) {
    id name status
  }
}

# Delete campaign (soft-delete)
mutation {
  deleteCampaign(id: "uuid-here")
}
```

### Content Pieces

```graphql
# Create a content piece
mutation {
  createContentPiece(input: {
    campaignId: "campaign-uuid",
    headline: "Amazing Offer",
    description: "Don't miss this deal",
    body: "Full content here...",
    language: "en"
  }) {
    id headline description body language state campaignId
  }
}

# List content pieces by campaign
query {
  contentPieces(campaignId: "campaign-uuid", page: 1, perPage: 20) {
    items { id headline language state }
    totalCount
  }
}

# Get single content piece
query {
  contentPiece(id: "piece-uuid") {
    id headline description body language state
  }
}

# Update content piece
mutation {
  updateContentPiece(id: "piece-uuid", input: { headline: "New Headline" }) {
    id headline
  }
}

# Delete content piece (soft-delete)
mutation {
  deleteContentPiece(id: "piece-uuid")
}
```

### AI Draft Generation

```graphql
# Generate AI draft from content brief
# Content must be in DRAFT state
mutation {
  generateDraft(contentId: "piece-uuid") {
    id headline description state
  }
}
```

### AI Translation

```graphql
# Translate content to another language
# Creates a new ContentPiece linked via originalId
# Supported: es, fr, de, pt, it, ja, zh
mutation {
  translateContent(contentId: "piece-uuid", targetLanguage: "es") {
    id headline description language state originalId
  }
}
```

### Review Actions

```graphql
# Approve content (from suggested_by_ai or reviewed state)
mutation {
  reviewContent(contentId: "piece-uuid", action: APPROVE) { id state }
}

# Reject content with feedback
mutation {
  reviewContent(contentId: "piece-uuid", action: REJECT, feedback: "Does not match brand voice") {
    id state
  }
}

# Request edits
mutation {
  reviewContent(contentId: "piece-uuid", action: REQUEST_EDITS, feedback: "Please revise tone") {
    id state
  }
}

# Edit rejected content (resets to draft)
mutation {
  editContent(contentId: "piece-uuid", headline: "New Headline", description: "New description") {
    id headline description state
  }
}

# View state history for audit trail
query {
  contentStateHistory(contentId: "piece-uuid") {
    fromState toState action feedback createdAt
  }
}
```

### Content States

Content pieces follow a state machine with valid transitions:

| From | To | Action |
|---|---|---|
| `DRAFT` | `SUGGESTED_BY_AI` | `generateDraft` |
| `SUGGESTED_BY_AI` | `APPROVED` | `reviewContent` with `APPROVE` |
| `SUGGESTED_BY_AI` | `REJECTED` | `reviewContent` with `REJECT` |
| `SUGGESTED_BY_AI` | `REVIEWED` | `reviewContent` with `REQUEST_EDITS` |
| `REVIEWED` | `APPROVED` | `reviewContent` with `APPROVE` |
| `REVIEWED` | `REJECTED` | `reviewContent` with `REJECT` |
| `REVIEWED` | `REVIEWED` | `reviewContent` with `REQUEST_EDITS` |
| `REJECTED` | `DRAFT` | `editContent` (reset for revision) |
| `APPROVED` | — | Terminal state, no transitions |

## Real-time WebSocket

State changes are broadcast in real-time via Django Channels WebSockets.

### Connection

```
ws://localhost:8000/ws/content/{content_id}/
```

### Message format (server → client)

```json
{
  "type": "state.change",
  "payload": {
    "contentId": "uuid",
    "campaignId": "uuid",
    "oldState": "suggested_by_ai",
    "newState": "approved",
    "action": "approve",
    "timestamp": "2025-01-01T12:00:00+00:00"
  }
}
```

Events are broadcast automatically whenever a `StateHistory` record is created (AI draft generated, review action taken, translation created).

## Project Structure

```
├── backend/                      # Django + Strawberry GraphQL
│   ├── config/                   # Django project configuration
│   │   ├── settings/             # Base, development, production
│   │   ├── urls.py               # URL routing
│   │   ├── asgi.py               # ASGI (HTTP + WebSocket router)
│   │   └── wsgi.py               # WSGI (HTTP-only entry point)
│   ├── apps/
│   │   ├── campaigns/            # Campaign CRUD models + GraphQL
│   │   ├── content/              # ContentPiece models + GraphQL
│   │   ├── ai/                   # AI provider abstraction + dispatch
│   │   │   └── providers/        # OpenAI, Anthropic implementations
│   │   ├── reviews/              # Review state machine + state history
│   │   └── ws/                   # WebSocket consumer + signal broadcast
│   ├── tests/                    # End-to-end workflow tests
│   ├── manage.py
│   ├── Dockerfile
│   └── pyproject.toml            # Dependencies + tool config
│
├── frontend/                     # React + Vite + Tailwind CSS
│   ├── src/
│   │   ├── components/           # Reusable UI components
│   │   ├── hooks/                # Custom React hooks
│   │   ├── pages/                # Page components (Dashboard, Detail)
│   │   ├── services/             # API client + WebSocket service
│   │   └── types/                # TypeScript type definitions
│   ├── Dockerfile                # Multi-stage, nginx-served
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── agentic/                      # Agentic workflow ecosystem
│   ├── tasks/                    # Feature list + session progress
│   ├── runs/                     # Per-task execution artifacts
│   ├── knowledge/                # Conventions, decisions, learnings
│   └── skills/                   # Community skills
│
├── docs/
│   ├── adrs/                     # Architecture Decision Records (6)
│   └── workflows.md              # Workflow guide
│
├── compose.yml                   # Docker Compose (PostgreSQL + Backend + Frontend)
├── .env.example                  # Environment variable template
├── init.sh                       # Automated setup script
├── .github/workflows/ci.yml      # CI pipeline (ruff, mypy, pytest, vitest, Docker)
└── README.md                     # This file
```

## Documentation

- **Architecture Decision Records**: [`docs/adrs/`](docs/adrs/) — rationale for every major technology choice
- **Workflow Guide**: [`docs/workflows.md`](docs/workflows.md) — detailed workflow diagrams and process flows
- **Agentic Workflow**: [`agentic/AGENTS.md`](agentic/AGENTS.md) — task management, quality gates, and agent roles
- **CI Pipeline**: [`.github/workflows/ci.yml`](.github/workflows/ci.yml) — automated checks on every push and PR

## Contributing

### CI Pipeline

Every push and pull request runs the following checks via GitHub Actions:

| Job | Tool | What it checks |
|---|---|---|
| `ruff-lint` | `ruff check backend/` | Python code style and lint rules |
| `mypy-typecheck` | `mypy backend/` (strict) | Python type annotations |
| `pytest-backend` | `pytest --cov` | Django unit tests (with PostgreSQL service) |
| `vitest-frontend` | `vitest` | React component and hook tests |
| `docker-build` | `docker compose build` | Both images build successfully |

All jobs must pass before a PR can merge. Run the same checks locally:

```bash
# Backend
cd backend
uv sync
uv run ruff check .
uv run mypy .
uv run pytest --cov --no-header

# Frontend
cd frontend
pnpm install --frozen-lockfile
pnpm test

# Docker
docker compose build
```
