# ACME GLOBAL MEDIA — AI Content Workflow Platform

[![CI](https://github.com/alecastro-nan/fullstack-engineer-ai-content-workflow-challenge/actions/workflows/ci.yml/badge.svg)](https://github.com/alecastro-nan/fullstack-engineer-ai-content-workflow-challenge/actions/workflows/ci.yml)

A campaign content management system with AI-powered drafting, translation/localization, and human-in-the-loop review.

## Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Backend** | Django 5.1 + Strawberry GraphQL | Python, mature ORM, GraphQL-native |
| **Frontend** | React 19 + Vite 6 + React Router 7 | Fast dev server, component-based UI |
| **Database** | PostgreSQL 16 (primary) | ACID, JSONB for AI metadata |
| **Real-time** | Django Channels (WebSocket) | State change broadcasts |
| **AI** | OpenAI SDK / Anthropic SDK | Provider abstraction with fallback |
| **Containers** | Docker + Docker Compose | One-command local setup |
| **Package Mgmt** | uv (Python) / pnpm (Frontend) | Fast, deterministic installs |

## Architecture

```
┌─ Frontend (Vite + React) ─────────────────────┐
│  Campaign Dashboard → Campaign Detail →        │
│  AI Draft Panel → Review UI → Translation      │
└────────────────────┬───────────────────────────┘
                     │ GraphQL (HTTP) + WebSocket
                     ▼
┌─ Backend (Django + Strawberry GraphQL) ────────┐
│  campaigns app → content app → ai app →        │
│                 reviews app                     │
│  ASGI: HTTP /graphql + WS /ws/content/          │
└────────────────────┬───────────────────────────┘
                     │
                     ▼
┌─ Infrastructure ───────────────────────────────┐
│  PostgreSQL 16 ← Redis (optional, for Channels) │
└─────────────────────────────────────────────────┘
```

## Current Status

### Implemented ✅

- **Campaign CRUD** (F-003): Create, read, update, soft-delete campaigns via GraphQL
- **ContentPiece CRUD** (F-004): Create, read, update, soft-delete content pieces within a campaign via GraphQL
- **Review State Machine** (F-008): State transitions with guards, approve/reject/request_edits mutations, full history audit trail
- **Health check** endpoint at `/graphql`

### In Progress 🔄

- AI provider abstraction layer (OpenAI + Anthropic)
- Frontend Dockerfile + Docker Compose finalization (F-006, F-007)

### Planned 📋

- AI draft generation
- AI translation/localization
- Real-time WebSocket broadcasts
- Full React frontend

## How to Run

### Prerequisites

- Python ≥3.12, uv, Node.js ≥18, pnpm, Docker ≥24

### Option 1: Manual (for development)

```bash
# 1. Install backend dependencies
cd backend
uv venv .venv && source .venv/bin/activate && uv sync

# 2. Install frontend dependencies
cd ../frontend && pnpm install

# 3. Create .env from template
cd .. && cp .env.example .env  # edit with your API keys

# 4. Start PostgreSQL
docker compose up db -d

# 5. Run migrations
cd backend && source .venv/bin/activate && python manage.py migrate

# 6. Start backend
python manage.py runserver

# 7. In another terminal, start frontend
cd frontend && pnpm dev
```

### Option 2: Docker Compose (full stack)

```bash
docker compose up --build
```

### Option 3: Automated init script

```bash
./init.sh
```

## GraphQL API

All API endpoints are available at `http://localhost:8000/graphql` with an interactive GraphQL playground in development mode.

### Campaigns

```graphql
# Create a campaign
mutation {
  createCampaign(input: { name: "Summer Campaign", description: "Q3 marketing" }) {
    id
    name
    description
    status
    createdAt
    updatedAt
  }
}

# List campaigns (paginated)
query {
  campaigns(page: 1, perPage: 20) {
    items { id name description status createdAt }
    totalCount
    page
    perPage
  }
}

# Get single campaign
query {
  campaign(id: "uuid-here") {
    id
    name
    description
    status
  }
}

# Update campaign
mutation {
  updateCampaign(id: "uuid-here", input: { name: "Updated Name", status: ARCHIVED }) {
    id
    name
    status
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
    id
    headline
    description
    body
    language
    state
    campaignId
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
    id
    headline
    description
    body
    language
    state
  }
}

# Update content piece
mutation {
  updateContentPiece(id: "piece-uuid", input: { headline: "New Headline" }) {
    id
    headline
  }
}

# Delete content piece (soft-delete)
mutation {
  deleteContentPiece(id: "piece-uuid")
}
```

### Review Actions

```graphql
# Approve content (from suggested_by_ai or reviewed state)
mutation {
  reviewContent(contentId: "piece-uuid", action: APPROVE) {
    id
    state
  }
}

# Reject content with feedback
mutation {
  reviewContent(contentId: "piece-uuid", action: REJECT, feedback: "Does not match brand voice") {
    id
    state
  }
}

# Request edits
mutation {
  reviewContent(contentId: "piece-uuid", action: REQUEST_EDITS, feedback: "Please revise tone") {
    id
    state
  }
}

# Edit rejected content (resets to draft)
mutation {
  editContent(contentId: "piece-uuid", headline: "New Headline", description: "New description") {
    id
    headline
    description
    state
  }
}

# View state history for audit trail
query {
  contentStateHistory(contentId: "piece-uuid") {
    fromState
    toState
    action
    feedback
    createdAt
  }
}
```

### Content States

Content pieces follow a state machine with valid transitions:

| From | To | Action |
|---|---|---|
| `DRAFT` | `SUGGESTED_BY_AI` | AI draft generation (F-010) |
| `SUGGESTED_BY_AI` | `APPROVED` | `reviewContent` with `APPROVE` |
| `SUGGESTED_BY_AI` | `REJECTED` | `reviewContent` with `REJECT` |
| `SUGGESTED_BY_AI` | `REVIEWED` | `reviewContent` with `REQUEST_EDITS` |
| `REVIEWED` | `APPROVED` | `reviewContent` with `APPROVE` |
| `REVIEWED` | `REJECTED` | `reviewContent` with `REJECT` |
| `REVIEWED` | `REVIEWED` | `reviewContent` with `REQUEST_EDITS` |
| `REJECTED` | `DRAFT` | `editContent` (reset for revision) |
| `APPROVED` | — | Terminal state, no transitions |

## Documentation

- **Architecture Decision Records**: [`docs/adrs/`](docs/adrs/) — rationale for tech choices
- **Architecture Overview**: [`docs/architecture-review.md`](docs/architecture-review.md)
- **Workflow Guide**: [`docs/workflows.md`](docs/workflows.md)
- **Agentic Workflow**: [`agentic/AGENTS.md`](agentic/AGENTS.md) — task management and quality gates

## Project Structure

```
backend/          # Django + Strawberry GraphQL
frontend/         # React + Vite
agentic/          # Agent workflow ecosystem (tasks, runs, decisions)
docs/             # ADRs, architecture, workflow docs
compose.yml       # Docker Compose
.env.example      # Environment template
init.sh           # Setup script
```

## Contributing

### CI Pipeline

Every push and pull request runs the following checks via GitHub Actions:

| Job | Tool | What it checks |
|---|---|---|
| `ruff-lint` | ruff | Python code style and lint rules |
| `mypy-typecheck` | mypy | Python type annotations (strict mode) |
| `pytest-backend` | pytest + coverage | Django unit tests (requires PostgreSQL service) |
| `vitest-frontend` | vitest | React component and hook tests |
| `docker-build` | Docker Compose | Both backend and frontend images build successfully |

All jobs must pass before a PR can merge. The pipeline typically completes in under 5 minutes.

Run the same checks locally:

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
