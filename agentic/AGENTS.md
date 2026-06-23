# ACME Content Workflow — Agentic Development Plan

> **Source of truth for AI agents building the NaN Labs Fullstack Engineer Challenge.**
> This document governs all agent behavior, task execution, handoffs, and quality gates.
> Symlinked: `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Agent Roles & Responsibilities](#2-agent-roles--responsibilities)
3. [Non-Negotiable Rules](#3-non-negotiable-rules)
4. [Environment Setup](#4-environment-setup)
5. [Monorepo Folder Structure](#5-monorepo-folder-structure)
6. [Feature List — Atomic Tasks](#6-feature-list--atomic-tasks)
7. [Agent Workflows & Handoff Protocol](#7-agent-workflows--handoff-protocol)
8. [Task Lifecycle & Done Criteria](#8-task-lifecycle--done-criteria)
9. [Testing Requirements](#9-testing-requirements)
10. [Architecture Decision Records](#10-architecture-decision-records)
11. [Knowledge Management](#11-knowledge-management)
12. [Human Decision Points](#12-human-decision-points)

---

## 1. Project Overview

| Field | Value |
|---|---|
| **Project** | ACME GLOBAL MEDIA — AI Content Workflow Platform |
| **Repository** | `fullstack-engineer-ai-content-workflow-challenge` |
| **Organization** | NaN Labs (NaN LABS S.A.) |
| **License** | MIT |
| **Primary Language** | English (all code, docs, commits, comments) |
| **Goal** | Build a campaign content management system with AI-powered drafting, translation/localization, and human-in-the-loop review — running fully in Docker. |

### Core Workflow

```
User creates Campaign
  └─> User adds Content Pieces (with brief)
       └─> Agent generates AI Draft (OpenAI / Anthropic)
            ├─> Human reviews draft → Approve / Edit / Reject
            └─> Human requests Translation → AI translates → Human reviews
```

### State Machine

```
[Draft] ──generate AI──> [Suggested by AI]
                              │
                   ┌──────────┼──────────┐
                   ▼          ▼          ▼
              [Reviewed]  [Edited]   [Rejected]
                   │
                   ▼
             [Approved]
```

---

## 2. Agent Roles & Responsibilities

Each role is defined using the **TDPC framework** (Title, Domain, Priority, Communication). All agents share the same AGENTS.md context.

### 2.1 Tech Lead — `@tech-lead`

| Attribute | Value |
|---|---|
| **Title** | Tech Lead / Architect |
| **Domain** | System design, data modeling, API contracts, technology choices |
| **Priority** | First — must plan before any code is written |
| **Communication** | Produces ADRs, data models, API specs, task breakdowns |

**Responsibilities:**
- Design the database schema (PostgreSQL tables, enums, indices)
- Define API contract (REST endpoints or GraphQL schema)
- Choose real-time mechanism (WebSockets vs SSE vs GraphQL Subscriptions)
- Select AI provider abstraction layer (OpenAI vs Anthropic vs both)
- Break down work into atomic tasks in `agentic/tasks/feature_list.json`
- Review all ADRs before implementation begins

**Triggers:**
- `"@tech-lead plan the database schema for campaigns"`
- `"@tech-lead create the API contract"`
- `"@tech-lead review the feature list"`

### 2.2 Builder — `@builder`

| Attribute | Value |
|---|---|
| **Title** | Implementation Engineer |
| **Domain** | Writing production code (backend, frontend, infra) |
| **Priority** | Second — executes tasks from `agentic/tasks/feature_list.json` |
| **Communication** | Updates `agentic/tasks/session-progress.md` after each task; commits code; documents decisions in `agentic/knowledge/decisions/` |

**Responsibilities:**
- Implement backend API endpoints, database models, migrations
- Build React frontend components, pages, state management
- Write Docker Compose, Dockerfiles, and env configuration
- Implement AI integrations (OpenAI SDK, Anthropic SDK)
- Add WebSocket / SSE real-time broadcasting
- Write unit tests and integration tests alongside code
- **Update documentation** — README.md, docs/architecture.md, and any `.md` files affected by the change must be updated in the same commit as the code

**Triggers:**
- `"@builder take task F-001 from feature_list.json and implement it"`
- `"@builder implement the Campaign CRUD API"`
- `"@builder create the React campaign dashboard component"`

### 2.3 Code Reviewer — `@code-reviewer`

| Attribute | Value |
|---|---|
| **Title** | Code Quality Guardian |
| **Domain** | Code review, linting, type checking, best practices |
| **Priority** | After Builder completes a feature |
| **Communication** | Files review comments in `agentic/tasks/session-progress.md`; blocks promotion if quality gates fail |

**Responsibilities:**
- Review all code for correctness, style, and adherence to AGENTS.md
- Verify TypeScript types / Python type hints are strict
- Check that error handling, logging, and env validation exist
- Ensure no secrets (API keys) are hardcoded or committed
- Confirm unit tests exist and pass
- Block merge if any quality gate fails

**Triggers:**
- `"@code-reviewer review the last batch of commits"`
- `"@code-reviewer validate PR quality gates"`

### 2.4 Security Reviewer — `@security-reviewer`

| Attribute | Value |
|---|---|
| **Title** | Security Auditor |
| **Domain** | API key management, input validation, XSS, CSRF, injection |
| **Priority** | After Code Reviewer |
| **Communication** | Produces security notes in `agentic/knowledge/decisions/` and updates `agentic/tasks/session-progress.md` |

**Responsibilities:**
- Verify API keys are loaded from environment (never hardcoded)
- Validate all user inputs server-side (sanitization, escaping)
- Ensure no sensitive data in client-side bundles or logs
- Check that Docker images don't run as root
- Review authentication/authorization if implemented

**Triggers:**
- `"@security-reviewer audit the AI integration code for API key leaks"`
- `"@security-reviewer check the Docker setup for security best practices"`

### 2.5 TDD Guide — `@tdd-guide`

| Attribute | Value |
|---|---|
| **Title** | Test-Driven Development Coach |
| **Domain** | Writing tests before implementation, coverage enforcement |
| **Priority** | Before Builder starts a feature |
| **Communication** | Writes test stubs in `agentic/tasks/feature_list.json`; reviews test quality |

**Responsibilities:**
- Define what tests are needed for each feature before coding
- Ensure tests cover: success path, error path, edge cases, AI failures
- Validate coverage meets threshold (≥80% for core logic)
- Check that tests are meaningful (not just "test exists")

**Triggers:**
- `"@tdd-guide define tests for F-002 (AI Draft Generation)"`
- `"@tdd-guide review test coverage for the backend module"`

### 2.6 Planner — `@planner`

| Attribute | Value |
|---|---|
| **Title** | Task & Feature Planner |
| **Domain** | Breaking down requirements into atomic, ordered tasks |
| **Priority** | After Tech Lead, before Builder |
| **Communication** | Maintains `agentic/tasks/feature_list.json`; adds acceptance criteria to each task |

**Responsibilities:**
- Decompose the challenge into fine-grained atomic tasks
- Assign dependencies and ordering
- Define explicit "done" criteria for each task
- Track overall progress in `agentic/tasks/feature_list.json`

**Triggers:**
- `"@planner break the challenge into atomic tasks"`
- `"@planner reorder tasks based on dependency graph"`

### 2.7 Database Reviewer — `@database-reviewer`

| Attribute | Value |
|---|---|
| **Title** | Schema & Query Specialist |
| **Domain** | PostgreSQL schema design, migrations, indexing, query performance |
| **Priority** | After Tech Lead produces schema |
| **Communication** | Reviews schema before migration runs; flags in `agentic/tasks/session-progress.md` |

**Responsibilities:**
- Review PostgreSQL schema for normalization, indexing, foreign keys
- Check migration files for reversibility and idempotency
- Verify N+1 query problems are avoided (use eager loading / JOINs)
- Confirm enum types for review states are used

**Triggers:**
- `"@database-reviewer review the campaign schema before migration"`
- `"@database-reviewer check the query pattern for campaign listing"`

---

## 3. Non-Negotiable Rules

> Violating any of these rules causes automatic rejection of the submission. These are **hard constraints**.

### 3.1 Technology

| # | Rule | Why |
|---|---|---|
| R-001 | Backend must be Django (Python) with Strawberry GraphQL. | Challenge requirement |
| R-002 | Frontend must be React (Next.js, Remix, or Vite). | Challenge requirement |
| R-003 | Database must be PostgreSQL. MongoDB is optional supplement only. | Challenge requirement |
| R-004 | Docker Compose must run the entire stack locally with one command. | Challenge requirement |
| R-005 | Must integrate at least one of: OpenAI SDK or Anthropic SDK. | Challenge requirement |
| R-006 | State machine must track: Draft → Suggested by AI → Reviewed → Approved / Rejected. | Challenge requirement |
| R-007 | No hardcoded secrets. All API keys, DB passwords, secrets via environment variables. | Security |

### 3.2 Code Quality

| # | Rule | Why |
|---|---|---|
| R-008 | Every backend endpoint must have at least one unit test. | Evaluation criterion |
| R-009 | Every AI integration must have a mock-based unit test (no real API calls in unit tests). | CI reliability |
| R-010 | All Python code must have strict type hints (PEP 484). Use `mypy` for static type checking. | NaN Labs standard |
| R-011 | No `Any` types in Python. Use proper type annotations, Protocols, or Generics. | Type safety |
| R-012 | Every function must handle errors explicitly — no silent `try/catch` with empty block. | Reliability |
| R-013 | All commits must use conventional commits format: `type(scope): message`. | Traceability |
| R-014 | No `print()` in production code. Use Django's built-in logging or structlog. | Production readiness |

### 3.3 Process

| # | Rule | Why |
|---|---|---|
| R-015 | ADR must be written for: REST vs GraphQL, AI provider choice, real-time mechanism, and DB schema. | Challenge requires justification |
| R-016 | `agentic/tasks/session-progress.md` must be updated after every task completion with: what was done, what failed, next task. | Handoff protocol |
| R-017 | No task can skip Code Review gate. Builder must wait for `@code-reviewer` sign-off before moving to next task. | Quality gate |
| R-018 | Feature must be testable in isolation before marking done (manual or automated). | Done criteria |
| R-019 | AGENTS.md is the single source of truth. If conflicting instructions exist elsewhere, AGENTS.md wins. | Governance |
| R-026 | Branch naming must follow `type/task-id-short-description` (see `agentic/knowledge/conventions/branch-naming.md`). `feat/agentic-plan` is the integration branch — always branch from it. | Traceability |
| R-027 | Never merge open PRs without explicit human approval. Always ask before merging any pull request. | Governance |

### 3.4 Documentation

| # | Rule | Why |
|---|---|---|
| R-020 | Never commit to `main`/`master`. Work on feature branches, submit via PR. | Submission workflow |
| R-021 | Every PR must use the provided `.github/PULL_REQUEST_TEMPLATE.md`. | Challenge requirement |
| R-022 | `.env.example` must be committed (without real secrets). | Challenge requirement |
| R-023 | `compose.yml` must exist at root and work with `docker compose up`. | Challenge requirement |
| R-024 | `README.md` is a living document — updated after every feature task, not left for a final batch. | Supervisor visibility |
| R-025 | Every task must include a `documentation_requirements` section in its feature definition specifying what docs to update. | Traceability |

---

## 4. Environment Setup

### 4.1 Prerequisites (installed on host machine)

| Tool | Version | Purpose |
|---|---|---|
| Python | ≥3.12 | Backend (Django + Strawberry GraphQL) runtime |
| Node.js | ≥18 LTS | Frontend (React/Vite) runtime |
| uv | ≥0.5.x | Python package manager (preferred over pip) |
| Docker | ≥24.x | Containerization (required) |
| Docker Compose | ≥2.24.x | Multi-container orchestration |
| psql | ≥16.x | Direct DB inspection and troubleshooting |
| gh | ≥2.x | GitHub CLI — PR creation, CI checks |
| jq | ≥1.7 | JSON parsing in shell scripts |

### 4.2 Init Script — `init.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== ACME Challenge — Environment Initialization ==="

# 1. Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "Python ≥3.12 is required"; exit 1; }
command -v uv >/dev/null 2>&1 || { echo "uv is required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js is required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker is required"; exit 1; }

# 2. Install backend dependencies
echo "[backend] Installing dependencies..."
cd backend
uv venv .venv && source .venv/bin/activate && uv sync
cd ..

# 3. Install frontend dependencies
echo "[frontend] Installing dependencies..."
cd frontend
corepack enable && pnpm install
cd ..

# 4. Create .env from example if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from .env.example — edit with your API keys"
fi

# 5. Start infrastructure (PostgreSQL, Redis if applicable)
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
```

### 4.3 Environment Variables — `.env.example`

```env
# ── Database ──
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/acme

# ── AI Providers (at least one required) ──
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# ── App ──
DJANGO_SETTINGS_MODULE=config.settings.development
PORT=8000
FRONTEND_URL=http://localhost:5173
DEBUG=True

# ── Redis (optional, for async/queues) ──
REDIS_URL=redis://localhost:6379
```

### 4.4 Skill Installation for Agents

Agent skills (`agentic/skills/`) are installed from community sources. All skills are audited with SkillSpector before installation — see `agentic/knowledge/decisions/002-remove-critical-skills.md` for the security audit history.

Each skill file must follow this template:

```markdown
# Skill: <name>

## Purpose
<one paragraph describing what this skill achieves>

## When to Use
<conditions that trigger this skill>

## Steps
1. <step-by-step instructions>
2. ...

## Verification
<how to verify the skill was applied correctly>

## Examples
<link to example code or ADR>
```

---

## 5. Monorepo Folder Structure

```
fullstack-engineer-ai-content-workflow-challenge/
│
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md        # PR template (already exists)
│   ├── copilot-instructions.md         # Symlink → ../../agentic/AGENTS.md
│   └── workflows/
│       └── ci.yml                      # GitHub Actions: lint, typecheck, test
│
├── agentic/                             # ← Agentic workflow ecosystem (canonical home)
│   ├── AGENTS.md                       # Source of truth (symlinked from root)
│   ├── skills/                          # Community skills (was .agents/skills/)
│   ├── tasks/
│   │   ├── feature_list.json           # Atomic task backlog (symlinked from root)
│   │   └── session-progress.md         # Session index (symlinked from root)
│   ├── knowledge/
│   │   ├── conventions/                # Coding standards (was knowledge/conventions/)
│   │   ├── decisions/                  # Minor design decisions (was knowledge/decisions/)
│   │   └── learnings/                  # Error learnings (was knowledge/learnings/)
│   ├── personas/                       # Agent role definitions (was harness/personas/)
│   ├── runs/                            # Per-task execution artifacts (was harness/workflows/runs/)
│   ├── evaluation/                      # Quality rubric + eval cases (was evaluation/)
│   ├── install-skills.sh               # Skill installer (symlinked from root)
│   ├── skills-lock.json                # Skill lockfile (symlinked from root)
│   └── run-task.sh                     # Task execution CLI
│
├── backend/                            # Backend application (Django + Strawberry GraphQL)
│   ├── config/                         # Django project configuration
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # Base settings (shared)
│   │   │   ├── development.py          # Dev overrides
│   │   │   └── production.py           # Production overrides
│   │   ├── urls.py                     # Root URL configuration
│   │   ├── wsgi.py
│   │   └── asgi.py                     # ASGI for WebSocket support
│   ├── manage.py                       # Django management
│   ├── Dockerfile
│   ├── pyproject.toml                  # Python dependencies
│   └── uv.lock                         # Lockfile for uv
│
├── frontend/                           # React application (Vite)
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── docs/
│   ├── adrs/                           # Architecture Decision Records
│   ├── architecture.md                 # High-level architecture diagram (Mermaid)
│   └── workflows.md                    # ASCII / Mermaid workflow diagrams
│
├── compose.yml                         # Docker Compose — PostgreSQL + Backend + Frontend
├── .env.example                        # Environment variable template (secrets excluded)
├── .gitignore
├── AGENTS.md → agentic/AGENTS.md       # Symlink (tool compatibility)
├── CLAUDE.md → AGENTS.md               # Symlink (Claude Code)
├── .cursorrules → AGENTS.md            # Symlink (Cursor AI)
├── feature_list.json → agentic/tasks/feature_list.json  # Symlink
├── session-progress.md → agentic/tasks/session-progress.md  # Symlink
├── install-skills.sh → agentic/install-skills.sh  # Symlink
├── skills-lock.json → agentic/skills-lock.json  # Symlink
├── init.sh                             # Environment initialization script
├── biome.json                          # Lint & format (Biome only for frontend)
└── README.md                           # Challenge description (source document)
```

---

## 6. Feature List — Atomic Tasks

> This is the complete breakdown of the challenge into atomic, independently testable tasks.
> Stored in `agentic/tasks/feature_list.json` with the following schema:

```json
{
  "id": "F-001",
  "title": "Campaign CRUD API",
  "description": "REST endpoints to create, read, update, delete campaigns",
  "dependencies": [],
  "stack": "backend",
  "role": "builder",
  "status": "pending",
  "acceptance_criteria": [
    "POST /api/campaigns creates a campaign and returns 201",
    "GET /api/campaigns returns paginated list of campaigns",
    "GET /api/campaigns/:id returns single campaign with content pieces",
    "PATCH /api/campaigns/:id updates campaign fields",
    "DELETE /api/campaigns/:id soft-deletes a campaign",
    "All endpoints return proper HTTP status codes on error",
    "Input validation rejects malformed payloads with 400",
    "Database migration creates campaigns table with: id, name, description, status, createdAt, updatedAt"
  ],
  "test_requirements": [
    "Unit test for campaign service: create, findAll, findOne, update, remove",
    "Integration test for each endpoint (REQUEST → RESPONSE validation)",
    "Test validation pipe rejects empty name and unknown fields"
  ],
  "documentation_requirements": [
    "README.md: add new API endpoints to GraphQL reference section",
    "docs/architecture.md: update workflow diagram if new states were added"
  ],
  "done_when": [
    "All acceptance criteria pass",
    "All tests pass (≥80% coverage on module)",
    "Code reviewer has approved",
    "Security reviewer has confirmed no secrets exposed",
    "API can be tested manually via curl or Swagger"
  ]
}
```

### Feature List — All Tasks

| ID | Title | Deps | Stack | Est. Time |
|---|---|---|---|---|
| **Phase 0: Foundation** |
| F-000 | Initialize monorepo: folder structure, configs, symlinks | — | infra | 15min |
| F-001 | Campaign CRUD API | F-000 | backend | 45min |
| F-002 | Content Piece CRUD API | F-001 | backend | 45min |
| F-003 | PostgreSQL schema & migrations | F-000 | backend | 30min |
| **Phase 1: AI Integration** |
| F-004 | AI provider abstraction layer (OpenAI + Anthropic) | F-000 | backend | 45min |
| F-005 | AI draft generation endpoint | F-002, F-004 | backend | 45min |
| F-006 | AI translation/localization endpoint | F-002, F-004 | backend | 45min |
| **Phase 2: Review Workflow** |
| F-007 | Review state machine (state transitions, guards) | F-002 | backend | 30min |
| F-008 | Review endpoints (approve, reject, request edits) | F-007 | backend | 30min |
| **Phase 3: Real-time** |
| F-009 | WebSocket/SSE setup in backend | F-000 | backend | 30min |
| F-010 | Real-time broadcast on state changes | F-008, F-009 | backend | 30min |
| **Phase 4: Frontend** |
| F-011 | React project scaffold (Vite, routing, API client) | F-000 | frontend | 30min |
| F-012 | Campaign Dashboard page (list + create) | F-001, F-011 | frontend | 45min |
| F-013 | Campaign Detail page (content pieces, states) | F-002, F-012 | frontend | 45min |
| F-014 | AI Draft panel (trigger generation, preview) | F-005, F-013 | frontend | 45min |
| F-015 | Review UI (approve/reject/edit buttons, state badges) | F-008, F-013 | frontend | 30min |
| F-016 | Translation panel (select language, trigger, preview) | F-006, F-013 | frontend | 45min |
| F-017 | Real-time status updates on frontend | F-010, F-011 | frontend | 30min |
| **Phase 5: Infrastructure** |
| F-018 | Docker Compose (PostgreSQL + Backend + Frontend) | F-001, F-011 | infra | 30min |
| F-019 | Dockerfiles (backend + frontend multi-stage) | F-018 | infra | 30min |
| F-020 | GitHub Actions CI (lint, typecheck, test) | F-019 | infra | 30min |
| **Phase 6: Quality & Polish** |
| F-021 | End-to-end workflow test (Campaign → Content → AI Draft → Review) | All above | test | 45min |
| F-022 | ADRs (REST vs GraphQL, AI provider, real-time, DB schema) | All above | docs | 30min |
| F-023 | README update (setup instructions, tech decisions, tradeoffs) | F-022 | docs | 30min |
| F-024 | Final smoke test and PR creation | F-023 | infra | 15min |

**Total estimated time: ~13 hours** (single developer with agents can parallelize phases 1-4)

---

## 7. Agent Workflows & Handoff Protocol

### 7.1 Task Execution Flow

```
  ┌──────────┐     ┌──────────┐     ┌──────────────┐     ┌──────────────────┐
  │ Planner  │────>│ TechLead │────>│  TDD Guide   │────>│     Builder      │
  │ creates  │     │ approves │     │ writes test  │     │ implements code  │
  │ tasks    │     │ design   │     │ stubs        │     │ + tests + docs   │
  └──────────┘     └──────────┘     └──────────────┘     └────────┬─────────┘
                                                                   │
                        ┌─────────────────────<────────────────────┘
                        ▼
              ┌──────────────────┐     ┌──────────────┐     ┌──────────────┐
              │  Code Reviewer   │────>│ Security Rev │────>│  DB Reviewer │
              │ reviews code +   │     │ audits sec   │     │ reviews schema│
              │ tests + docs     │     │ concerns     │     │ + queries     │
              └────────┬─────────┘     └──────────────┘     └──────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │   Mark DONE in   │
              │ feature_list.json│
              │  + update        │
              │ claude-progress  │
              └──────────────────┘
```

### 7.2 Handoff Protocol

Each task gets its **own handoff directory** under `agentic/runs/F-XXX-task-name/`. This keeps context small — agents only read what's relevant.

### 7.2.1 Run Directory Structure

```
agentic/runs/
├── F-001-campaign-crud/
│   ├── handoff.md       # Handoff FROM builder TO reviewer
│   ├── plan.md          # Tech Lead's pre-implementation plan
│   └── audit.log        # Raw command outputs, timestamps, errors
└── F-002-content-crud/
    └── ...
```

### 7.2.2 `agentic/tasks/session-progress.md` — Lightweight Index Only

`agentic/tasks/session-progress.md` is NOT a handoff dump. It is a **1-2 line summary per task** that points to the detailed handoff:

```markdown
## F-001 Campaign CRUD API — DONE
handoff → `agentic/runs/F-001-campaign-crud/handoff.md`
reviewers: @code-reviewer ✅ @security-reviewer ✅

## F-002 Content Piece CRUD API — IN REVIEW
handoff → `agentic/runs/F-002-content-crud/handoff.md`
reviewers: @code-reviewer ⏳
```

### 7.2.3 Handoff Template (`handoff.md`)

```markdown
# Handoff — F-001: Campaign CRUD API
## Meta
- **From:** Builder
- **To:** Code Reviewer
- **Date:** 2025-01-01 14:00 UTC

## What was done
- POST /api/campaigns — creates campaign (tested)
- GET /api/campaigns — paginated list (tested)
- GET /api/campaigns/:id — single with content (tested)
- PATCH /api/campaigns/:id — partial update (tested)
- DELETE /api/campaigns/:id — soft delete (tested)

## Documentation updated
- README.md: added GraphQL API reference for campaigns section
- docs/architecture.md: updated workflow diagram

## Not done / known issues
- Swagger UI not added (out of scope)

## Next actions
1. Code Reviewer: review `backend/campaign/`, verify docs changes
2. Security Reviewer: verify env var handling

## Artifacts
- Migration: `backend/drizzle/0000_init/`
- Decision: `agentic/knowledge/decisions/001-campaign-soft-delete.md`
```

### 7.4 Subagent Delegation Strategy

Not all NaNLABS subagents provide equal value for this challenge. The following table defines when each subagent should be invoked during task execution, based on the task's stack, complexity, and quality gate requirements.

#### 7.4.1 Active Subagents (7 of 16)

| Subagent | When | Why | Required |
|---|---|---|---|
| `@nanlabs-planner` | Start of complex tasks (>45min) or new phases | Breaks down work into atomic steps with risk assessment | No |
| `@nanlabs-tdd-guide` | Before implementing any backend feature (F-003, F-004, F-006–F-010) | Writes test stubs first per R-008/R-009 (every endpoint + AI mock tests) | Yes (pre-implementation) |
| `@nanlabs-code-reviewer` | After every backend or frontend feature task | Mandated by R-017 — no task skips code review | Yes |
| `@nanlabs-security-reviewer` | After code review for any task touching API keys, user input, or data | Mandated by R-007 — no hardcoded secrets | Yes |
| `@nanlabs-database-reviewer` | During F-003/F-004 (schema) and F-009 (state machine) | Reviews schema design, indices, N+1 prevention, migration idempotency | Yes (when DB changes) |
| `@nanlabs-typescript-reviewer` | After every frontend task (F-013 through F-019) | Type safety for React/TypeScript components and hooks | Yes (frontend only) |
| `@nanlabs-e2e-runner` | During F-023 (end-to-end workflow test) | Playwright E2E test for full Campaign→Content→AI→Review workflow | Yes |

#### 7.4.2 Inactive Subagents (9 of 16)

These subagents are intentionally excluded for this challenge:

| Subagent | Reason for Exclusion |
|---|---|
| `@nanlabs-performance-optimizer` | No performance benchmarks or latency requirements in scope |
| `@nanlabs-refactor-cleaner` | All code is greenfield — no technical debt to remediate |
| `@nanlabs-tech-assistant` | NaNLABS internal ops procedures, not relevant to ACME challenge |
| `@nanlabs-client-workflow-bootstrap` | Workflow already configured and documented |
| `@nanlabs-reference-lookup` | AGENTS.md is the single source of truth (R-019) |
| `@nanlabs-docs-lookup` | Django/Strawberry/Apollo docs are well-known and directly accessible |
| `@nanlabs-build-error-resolver` | Reactive only — invoke if a build/CI error occurs |
| `@nanlabs-assistant` | Redundant — AGENTS.md already provides full context |
| `@nanlabs-architect` | Invoked once per phase for structural decisions, not per-task |

#### 7.4.3 Task Execution Flow by Type

**Backend feature task (F-003, F-004, F-006, F-007, F-008, F-009, F-010):**
```
@planner(?) → @tdd-guide → Builder → @database-reviewer(?) → @code-reviewer → @security-reviewer → Doc update → done
  optional      required     code       if DB changes            required        required         Builder
```

**Frontend feature task (F-013, F-014, F-015, F-016, F-017, F-018, F-019):**
```
@planner(?) → Builder → @typescript-reviewer → @code-reviewer → Doc update → done
  optional               required              required         Builder
```

**Infrastructure task (F-020, F-021, F-022):**
```
Builder → @code-reviewer → @security-reviewer → Doc update → done
           required          required            Builder
```

**E2E / Quality task (F-023):**
```
@e2e-runner → @code-reviewer → Doc update → done
  required     required        Builder
```

#### 7.4.4 Quality Gate Mapping

| Gate | Subagent | Enforced |
|---|---|---|
| R-007 (no hardcoded secrets) | `@security-reviewer` | Every task |
| R-008 (unit tests per endpoint) | `@tdd-guide` + `@code-reviewer` | Every backend task |
| R-009 (AI mock tests) | `@tdd-guide` + `@code-reviewer` | F-006, F-007, F-008 |
| R-010 (strict type hints) | `@typescript-reviewer` (frontend), mypy (backend) | Every task |
| R-017 (code review gate) | `@code-reviewer` | Every task |
| R-024 (README updated) | `@code-reviewer` | Every task — code reviewer verifies docs were updated |
| R-025 (doc requirements exist) | `@code-reviewer` | Every task — code reviewer verifies documentation_requirements are defined |

#### 7.4.5 Reference

Full subagent definitions with purpose, triggers, and verification steps are documented at `agentic/knowledge/conventions/subagent-workflow.md`.

### 7.5 Error Recovery Protocol

When a task fails:

1. **Builder** logs the error in `agentic/knowledge/learnings/` with timestamp
2. **Builder** creates a new attempt in `agentic/tasks/feature_list.json` (bump `attempt` counter)
3. **Builder** logs the error in the task's `audit.log` under `agentic/runs/F-XXX/`, and updates `agentic/tasks/session-progress.md` with "BLOCKED" status
4. **Tech Lead** reviews and may change the approach (new ADR if needed)
5. **Builder** retries with amended plan

---

## 8. Task Lifecycle & Done Criteria

### 8.1 Task States in `agentic/tasks/feature_list.json`

| State | Meaning |
|---|---|
| `pending` | Not yet started, available for assignment |
| `in-progress` | Builder is actively implementing |
| `review` | Builder done, waiting for Code Review |
| `security-review` | Passed Code Review, waiting for Security Review |
| `rework` | Review found issues, Builder is fixing |
| `done` | All gates passed, task is complete |
| `blocked` | Blocked by dependency or external factor |
| `cancelled` | No longer needed |

### 8.2 Done Criteria (ALL must be true)

A task is **DONE** only when:

1. **Code exists** in the correct directory structure
2. **All acceptance criteria** from `agentic/tasks/feature_list.json` pass
3. **Tests exist and pass** (unit + integration as specified)
4. **Code Reviewer approved** (no critical or major issues)
5. **Security Reviewer approved** (no exposed secrets, no injection vectors)
6. **Database Reviewer approved** (if DB schema changed — no N+1, proper indices)
7. **Manual verification** — task can be demonstrated via curl or UI
8. **Task run directory** created at `agentic/runs/F-XXX/` with `handoff.md`, `plan.md`, `audit.log`
9. **`agentic/tasks/session-progress.md` updated** with 1-2 line summary pointing to the run directory
10. **`agentic/knowledge/decisions/` updated** if any design choice was made during implementation
11. **`README.md` and relevant docs updated** — code reviewer verifies documentation changes match the `documentation_requirements` in the task definition

### 8.3 Definition of "Atomic"

A task is atomic when:
- It can be implemented independently (dependencies are only Phase 0 tasks)
- It can be tested in isolation (mock/stub all dependencies)
- It produces a single logical unit of value (e.g., "Campaign CRUD" not "Campaign CRUD + AI + Review")
- Estimated implementation time ≤ 45 minutes
- A human can verify it in under 2 minutes

---

## 9. Testing Requirements

### 9.1 Testing Philosophy

- **TDD where possible**: Write test stubs before implementation (enforced by TDD Guide role)
- **Mock external calls**: Never call real OpenAI/Anthropic APIs in unit tests
- **Test both paths**: Success and error (400, 401, 404, 500)
- **Coverage target**: ≥80% for backend service layer, ≥60% for frontend components

### 9.2 Test Types

| Type | Tool | Location | Target |
|---|---|---|---|
| Type | Tool | Location | Target |
|---|---|---|---|---|
| Unit (backend) | pytest | `backend/**/tests/` | Services, models, GraphQL resolvers |
| Unit (frontend) | Vitest + React Testing Library | `frontend/src/**/*.test.tsx` | Components, hooks, utils |
| Integration | pytest + Django TestClient | `backend/**/tests/` | Full GraphQL request→response |
| AI Mock | unittest.mock | In unit test files | AI service with mocked provider |
| DB | pytest-django | `backend/**/tests/` | Model layer with test database |

### 9.3 Test Pattern References

Full test examples are NOT inlined here. Instead, the skills in `agentic/skills/` contain runnable examples for:

- **AI service unit test** — mock provider pattern, fallback logic, error propagation
- **Frontend component test** — render + assert + fireEvent pattern with React Testing Library
- **E2E workflow test** — full cycle: create campaign → add content → AI draft → approve → verify state

**Rules for all tests:**
- Mock all AI providers — no real API calls in unit tests
- Test both success and error paths (400, 404, 500)
- No `console.log` in test output — use the test framework's assertion methods
- Coverage target: ≥80% backend service layer, ≥60% frontend components

---

## 10. Architecture Decision Records

### 10.1 Required ADRs

Every submission must include these ADRs (challenge requirement for justification):

| # | Title | Key Decision |
|---|---|---|
| ADR-001 | REST vs GraphQL | Which API style and why |
| ADR-002 | AI Provider Selection | OpenAI vs Anthropic vs both |
| ADR-003 | Real-Time Mechanism | WebSockets vs SSE vs GraphQL Subscriptions |
| ADR-004 | Database Schema | Campaign, Content, Review tables design |

### 10.2 ADR Template

Every ADR must follow this template:

```markdown
# ADR-{number}: {title}

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue that motivates this decision?

## Decision
What is the change being proposed?

## Consequences
### Positive
- {benefit 1}
- {benefit 2}

### Negative
- {tradeoff 1}
- {tradeoff 2}

## Alternatives Considered
- {alternative 1}: rejected because...
- {alternative 2}: rejected because...

## References
- {link to relevant docs or discussion}
```

### 10.3 Decision Logs (for minor decisions)

Minor decisions (not warranting a full ADR) are stored in `agentic/knowledge/decisions/`:

```markdown
# Decision: {date} - {title}

## Context
Brief context of the problem.

## Decision
What we chose.

## Rationale
Why we chose this over alternatives.
```

---

## 11. Knowledge Management

### 11.1 Conventions Directory

`agentic/knowledge/conventions/` documents team-wide coding standards. Created once, referenced by all agents.

Example — `agentic/knowledge/conventions/django-structure.md`:

```markdown
# Django App Structure Convention

Every Django app must contain:
- `models.py` — database models with type-annotated fields
- `schema.py` — Strawberry GraphQL types, queries, and mutations
- `mutations.py` — GraphQL mutation classes (if complex)
- `queries.py` — GraphQL query classes (if complex)
- `apps.py` — Django app configuration
- `admin.py` — Django admin registration
- `tests/` — pytest test files

Naming rules:
- Model methods: `create()`, `get_by_id()`, `update()`, `delete()`, `list_all()`
- GraphQL queries use `resolve_*` naming convention
- Mutations use `Mutation` suffix
- Always use type hints on all function signatures
```

### 11.2 Learnings Directory

When an agent encounters and resolves an error, they document it in `agentic/knowledge/learnings/` to prevent recurrence:

```markdown
# Learning: {date} - {issue title}

## Error
What went wrong (include error message).

## Root Cause
Why it happened.

## Solution
How it was fixed (include code snippet if applicable).

## Prevention
How to avoid this in the future.
```

---

## 12. Human Decision Points

These are questions that **cannot be decided by agents alone**. The human must make the call.

### 12.1 Technology Choices

| # | Question | Options | Deadline |
|---|---|---|---|
| H-001 | ~~Which backend framework?~~ | **DECIDED:** Django + Strawberry GraphQL | — |
| H-002 | Which AI provider(s)? | OpenAI only / Anthropic only / Both | Before Phase 1 |
| H-003 | Which React framework? | Vite / Next.js / Remix | Before Phase 4 |
| H-004 | ~~API style?~~ | **DECIDED:** Strawberry GraphQL (native GraphQL for Django) | — |
| H-005 | ~~ORM / Query builder?~~ | **DECIDED:** Django ORM (built-in, no external ORM) | — |
| H-006 | Real-time library? | Django Channels / SSE (Server-Sent Events) | During ADR-003 |
| H-007 | ~~Package manager?~~ | **DECIDED:** uv (Python) + pnpm (frontend) | — |
| H-008 | Test runner? | pytest (backend) / Vitest (frontend) | Before testing |

### 12.2 Design Decisions

| # | Question | Context |
|---|---|---|
| H-009 | Content piece schema: what fields? | Minimum: headline, description, language, state, campaignId. Optional: body, tags, keywords, tone, targetAudience. |
| H-010 | Multi-language support: how modeled? | Option A: separate content pieces per language (linked by `originalId`). Option B: single content piece with language variants. |
| H-011 | Soft delete vs hard delete for campaigns? | Challenge requires "Delete" — does it mean soft (isDeleted flag) or hard (remove row)? |
| H-012 | AI generation: synchronous or async (queue)? | Sync: wait for AI response (simple). Async: queue job, poll/subscribe for completion (better UX but more complex). |
| H-013 | Frontend state management? | React Context / Zustand / Redux Toolkit / TanStack Query |
| H-014 | Styling approach? | Tailwind CSS / styled-components / CSS Modules / plain CSS |

### 12.3 When to Ask

Agents must ask the human for a decision when:
1. A block `#` question has not been answered
2. Two or more ADRs conflict and human preference is needed
3. A task is blocked for > 15 minutes due to an ambiguity
4. The human explicitly requests to be consulted

---

## Appendices

### A. Quick Reference — File Symlinks

```bash
# Create symlinks so all agents see the same AGENTS.md
ln -sf ../../agentic/AGENTS.md .github/copilot-instructions.md
ln -sf agentic/AGENTS.md AGENTS.md
ln -sf AGENTS.md CLAUDE.md
ln -sf AGENTS.md .cursorrules
ln -sf agentic/tasks/feature_list.json feature_list.json
ln -sf agentic/tasks/session-progress.md session-progress.md
ln -sf agentic/install-skills.sh install-skills.sh
ln -sf agentic/skills-lock.json skills-lock.json
```

### B. Git Workflow

```bash
# Start a new feature branch
git checkout -b feat/campaign-crud-api

# Conventional commits
git commit -m "feat(api): add campaign CRUD endpoints"
git commit -m "test(api): add campaign service unit tests"
git commit -m "docs(adr): document REST vs GraphQL decision"

# Push and create PR
gh pr create --draft --title "feat: campaign CRUD API" --body-file .github/PULL_REQUEST_TEMPLATE.md
```

### C. Useful Commands

```bash
# Run all tests
cd backend && pnpm test
cd frontend && pnpm test

# Lint & format (Biome — frontend only)
pnpm biome check --write .

# Type check
cd backend && mypy .
cd frontend && pnpm typecheck

# Rebuild and restart Docker
docker compose down && docker compose up --build

# View PostgreSQL logs
docker compose logs -f db

# Connect to PostgreSQL
psql -h localhost -U postgres -d acme

# Open GraphQL playground
open http://localhost:8000/graphql
```

### D. State Machine — Valid Transitions

```python
# ReviewState enum
from enum import Enum

class ContentState(str, Enum):
    DRAFT = 'draft'
    SUGGESTED_BY_AI = 'suggested_by_ai'
    REVIEWED = 'reviewed'
    APPROVED = 'approved'
    REJECTED = 'rejected'

# Valid transitions map
VALID_TRANSITIONS: dict[ContentState, list[ContentState]] = {
    ContentState.DRAFT: [ContentState.SUGGESTED_BY_AI],
    ContentState.SUGGESTED_BY_AI: [ContentState.REVIEWED, ContentState.REJECTED],
    ContentState.REVIEWED: [ContentState.APPROVED, ContentState.REJECTED, ContentState.SUGGESTED_BY_AI],
    ContentState.APPROVED: [],
    ContentState.REJECTED: [ContentState.DRAFT, ContentState.SUGGESTED_BY_AI],
}
```

---

*This document is the single source of truth for all agents working on the ACME Content Workflow challenge. It is designed for ingestion into Google NotebookLM and use as system context for Claude, Cursor, Copilot, and other AI coding assistants.*
