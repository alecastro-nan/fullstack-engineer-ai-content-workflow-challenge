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
- Break down work into atomic tasks in `feature_list.json`
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
| **Priority** | Second — executes tasks from `feature_list.json` |
| **Communication** | Updates `session-progress.md` after each task; commits code; documents decisions in `/knowledge/decisions/` |

**Responsibilities:**
- Implement backend API endpoints, database models, migrations
- Build React frontend components, pages, state management
- Write Docker Compose, Dockerfiles, and env configuration
- Implement AI integrations (OpenAI SDK, Anthropic SDK)
- Add WebSocket / SSE real-time broadcasting
- Write unit tests and integration tests alongside code

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
| **Communication** | Files review comments in `session-progress.md`; blocks promotion if quality gates fail |

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
| **Communication** | Produces security notes in `/knowledge/decisions/` and updates `session-progress.md` |

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
| **Communication** | Writes test stubs in `feature_list.json`; reviews test quality |

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
| **Communication** | Maintains `feature_list.json`; adds acceptance criteria to each task |

**Responsibilities:**
- Decompose the challenge into fine-grained atomic tasks
- Assign dependencies and ordering
- Define explicit "done" criteria for each task
- Track overall progress in `feature_list.json`

**Triggers:**
- `"@planner break the challenge into atomic tasks"`
- `"@planner reorder tasks based on dependency graph"`

### 2.7 Database Reviewer — `@database-reviewer`

| Attribute | Value |
|---|---|
| **Title** | Schema & Query Specialist |
| **Domain** | PostgreSQL schema design, migrations, indexing, query performance |
| **Priority** | After Tech Lead produces schema |
| **Communication** | Reviews schema before migration runs; flags in `session-progress.md` |

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
| R-001 | Backend must be one of: NestJS (TypeScript), FastAPI (Python), or Fiber (Go). | Challenge requirement |
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
| R-010 | TypeScript code must have strict mode enabled. Python code must have type hints. | NaN Labs standard |
| R-011 | No `any` types in TypeScript. Use proper interfaces, types, or generics. | Type safety |
| R-012 | Every function must handle errors explicitly — no silent `try/catch` with empty block. | Reliability |
| R-013 | All commits must use conventional commits format: `type(scope): message`. | Traceability |
| R-014 | No `console.log` in production code. Use proper logger (e.g., Pino for NestJS, structlog for Python). | Production readiness |

### 3.3 Process

| # | Rule | Why |
|---|---|---|
| R-015 | ADR must be written for: REST vs GraphQL, AI provider choice, real-time mechanism, and DB schema. | Challenge requires justification |
| R-016 | `session-progress.md` must be updated after every task completion with: what was done, what failed, next task. | Handoff protocol |
| R-017 | No task can skip Code Review gate. Builder must wait for `@code-reviewer` sign-off before moving to next task. | Quality gate |
| R-018 | Feature must be testable in isolation before marking done (manual or automated). | Done criteria |
| R-019 | AGENTS.md is the single source of truth. If conflicting instructions exist elsewhere, AGENTS.md wins. | Governance |

### 3.4 Repository

| # | Rule | Why |
|---|---|---|
| R-020 | Never commit to `main`/`master`. Work on feature branches, submit via PR. | Submission workflow |
| R-021 | Every PR must use the provided `.github/PULL_REQUEST_TEMPLATE.md`. | Challenge requirement |
| R-022 | `.env.example` must be committed (without real secrets). | Challenge requirement |
| R-023 | `compose.yml` must exist at root and work with `docker compose up`. | Challenge requirement |

---

## 4. Environment Setup

### 4.1 Prerequisites (installed on host machine)

| Tool | Version | Purpose |
|---|---|---|
| Node.js | ≥18 LTS | Backend (NestJS) / Frontend (React/Vite) runtime |
| Python | ≥3.11 | Backend (FastAPI) alternative |
| Go | ≥1.22 | Backend (Fiber) alternative |
| pnpm | ≥9.x | Package manager (preferred over npm) |
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
command -v node >/dev/null 2>&1 || { echo "Node.js is required"; exit 1; }
command -v pnpm >/dev/null 2>&1 || { echo "pnpm is required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker is required"; exit 1; }

# 2. Install backend dependencies
echo "[backend] Installing dependencies..."
cd backend
if [ -f "package.json" ]; then
    pnpm install
elif [ -f "requirements.txt" ]; then
    python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
elif [ -f "go.mod" ]; then
    go mod download
fi
cd ..

# 3. Install frontend dependencies
echo "[frontend] Installing dependencies..."
cd frontend
pnpm install
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
cd backend
if [ -f "package.json" ]; then
    npx prisma migrate dev --name init 2>/dev/null || npx typeorm migration:run 2>/dev/null || true
elif [ -f "requirements.txt" ]; then
    python -m alembic upgrade head 2>/dev/null || true
fi
cd ..

# 7. Verify
echo "=== Environment ready ==="
echo "  Backend  → http://localhost:3000"
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
NODE_ENV=development
PORT=3000
FRONTEND_URL=http://localhost:5173

# ── Redis (optional, for async/queues) ──
REDIS_URL=redis://localhost:6379
```

### 4.4 Skill Installation for Agents

Skills are reusable procedure files stored in `harness/skills/`. Each skill is a markdown file teaching an agent how to perform a specific repeated task.

| Skill File | Purpose | Used By |
|---|---|---|
| `harness/skills/docker-setup.md` | How to write Dockerfiles and compose.yml for this project | Builder |
| `harness/skills/ai-integration.md` | How to abstract OpenAI/Anthropic calls, prompt templates, retries | Builder |
| `harness/skills/state-machine.md` | How to implement the review state machine (DB enum + guards) | Builder |
| `harness/skills/real-time.md` | How to set up WebSockets or SSE in chosen backend framework | Builder |
| `harness/skills/test-patterns.md` | How to write mock-based AI tests, NestJS e2e tests, React Testing Library | Builder, TDD Guide |
| `harness/skills/pr-submission.md` | How to create the PR with template, verify checklist, push | Builder |
| `harness/skills/migration-pattern.md` | How to create and run DB migrations (Prisma, TypeORM, Alembic) | Builder |

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
│   ├── PULL_REQUEST_TEMPLATE.md      # PR template (already exists)
│   ├── copilot-instructions.md       # Symlink → ../AGENTS.md
│   └── workflows/
│       └── ci.yml                    # GitHub Actions: lint, typecheck, test
│
├── backend/                          # Backend application (NestJS / FastAPI / Fiber)
│   ├── src/
│   │   ├── campaign/
│   │   │   ├── campaign.controller.ts
│   │   │   ├── campaign.service.ts
│   │   │   ├── campaign.module.ts
│   │   │   └── dto/
│   │   │       ├── create-campaign.dto.ts
│   │   │       └── update-campaign.dto.ts
│   │   ├── content/
│   │   │   ├── content.controller.ts
│   │   │   ├── content.service.ts
│   │   │   ├── content.module.ts
│   │   │   ├── entities/
│   │   │   │   └── content.entity.ts
│   │   │   └── dto/
│   │   │       ├── create-content.dto.ts
│   │   │       └── update-content.dto.ts
│   │   ├── ai/
│   │   │   ├── ai.module.ts
│   │   │   ├── ai.service.ts          # Abstraction over OpenAI/Anthropic
│   │   │   ├── providers/
│   │   │   │   ├── openai.provider.ts
│   │   │   │   └── anthropic.provider.ts
│   │   │   ├── prompts/
│   │   │   │   ├── draft.prompt.ts
│   │   │   │   └── translation.prompt.ts
│   │   │   └── dto/
│   │   │       ├── generate-draft.dto.ts
│   │   │       └── translate.dto.ts
│   │   ├── review/
│   │   │   ├── review.controller.ts
│   │   │   ├── review.service.ts
│   │   │   ├── review.module.ts
│   │   │   └── entities/
│   │   │       └── review-state.enum.ts
│   │   ├── realtime/
│   │   │   ├── realtime.gateway.ts      # WebSocket gateway
│   │   │   └── realtime.module.ts
│   │   ├── common/
│   │   │   ├── filters/
│   │   │   │   └── http-exception.filter.ts
│   │   │   ├── interceptors/
│   │   │   │   └── logging.interceptor.ts
│   │   │   └── pipes/
│   │   │       └── validation.pipe.ts
│   │   ├── app.module.ts
│   │   └── main.ts
│   ├── test/
│   │   ├── unit/
│   │   │   ├── campaign.service.spec.ts
│   │   │   ├── content.service.spec.ts
│   │   │   └── ai.service.spec.ts
│   │   └── e2e/
│   │       ├── campaign.e2e-spec.ts
│   │       └── content.e2e-spec.ts
│   ├── drizzle/                         # Drizzle ORM — schema definitions & migrations
│   │   └── schema.ts                    # Drizzle schema definitions
│   ├── Dockerfile
│   ├── package.json                    # Or requirements.txt / go.mod
│   ├── tsconfig.json                   # Or pyproject.toml
│   ├── biome.json                       # Lint & format config
│   └── .env.example
│
├── frontend/                           # React application (Vite / Next.js / Remix)
│   ├── src/
│   │   ├── components/
│   │   │   ├── CampaignList/
│   │   │   │   ├── CampaignList.tsx
│   │   │   │   └── CampaignList.test.tsx
│   │   │   ├── CampaignDetail/
│   │   │   │   ├── CampaignDetail.tsx
│   │   │   │   └── CampaignDetail.test.tsx
│   │   │   ├── ContentCard/
│   │   │   │   ├── ContentCard.tsx
│   │   │   │   └── ContentCard.test.tsx
│   │   │   ├── AIDraftPanel/
│   │   │   │   ├── AIDraftPanel.tsx
│   │   │   │   ├── AIDraftPanel.test.tsx
│   │   │   │   └── AIDraftPanel.stories.tsx
│   │   │   ├── ReviewActions/
│   │   │   │   ├── ReviewActions.tsx
│   │   │   │   └── ReviewActions.test.tsx
│   │   │   ├── TranslationPanel/
│   │   │   │   ├── TranslationPanel.tsx
│   │   │   │   └── TranslationPanel.test.tsx
│   │   │   └── RealtimeStatus/
│   │   │       ├── RealtimeStatus.tsx
│   │   │       └── RealtimeStatus.test.tsx
│   │   ├── hooks/
│   │   │   ├── useCampaigns.ts
│   │   │   ├── useContent.ts
│   │   │   ├── useRealtime.ts
│   │   │   └── useAIDraft.ts
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── CampaignPage.tsx
│   │   │   └── ContentEditor.tsx
│   │   ├── services/
│   │   │   ├── api.ts                  # Axios/fetch wrapper
│   │   │   └── websocket.ts
│   │   ├── types/
│   │   │   ├── campaign.ts
│   │   │   ├── content.ts
│   │   │   └── review.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   │   └── favicon.svg
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts                  # Or next.config.js / remix.config.js
│   └── .env.example
│
├── docs/
│   ├── adrs/
│   │   ├── ADR-001-rest-vs-graphql.md
│   │   ├── ADR-002-ai-provider.md
│   │   ├── ADR-003-real-time-mechanism.md
│   │   └── ADR-004-database-schema.md
│   ├── architecture.md                 # High-level architecture diagram (Mermaid)
│   └── workflows.md                    # ASCII / Mermaid workflow diagrams
│
├── knowledge/
│   ├── conventions/
│   │   ├── nestjs-structure.md         # How we organize NestJS modules
│   │   ├── react-component-patterns.md # How we write React components
│   │   └── commit-message-format.md    # Conventional commits reference
│   ├── decisions/
│   │   ├── 001-use-axios.md
│   │   └── 002-package-manager.md
│   └── learnings/
│       ├── 001-openai-rate-limit.md    # How we handled OpenAI rate limits
│       └── 002-docker-volume-perms.md  # Fixing Docker volume permission issues
│
├── harness/
│   ├── personas/
│   │   ├── tech-lead.md
│   │   ├── builder.md
│   │   ├── code-reviewer.md
│   │   ├── security-reviewer.md
│   │   ├── tdd-guide.md
│   │   ├── planner.md
│   │   └── database-reviewer.md
│   ├── skills/
│   │   ├── docker-setup.md
│   │   ├── ai-integration.md
│   │   ├── state-machine.md
│   │   ├── real-time.md
│   │   ├── test-patterns.md
│   │   ├── pr-submission.md
│   │   ├── migration-pattern.md
│   │   └── biome-setup.md                  # How to configure Biome for monorepo
│   └── workflows/
│       ├── run-task.sh                 # CLI to execute a single task with logging
│       └── runs/                       # Per-task execution artifacts
│           ├── F-001-campaign-crud/
│           │   ├── handoff.md          # Detailed handoff for this task
│           │   ├── plan.md             # Pre-implementation plan
│           │   └── audit.log           # Commands run, outputs, errors
│           ├── F-002-content-crud/
│           │   ├── handoff.md
│           │   ├── plan.md
│           │   └── audit.log
│           └── .gitkeep
│
├── evaluation/
│   ├── rubric.md                       # Quality rubric for code and prompts
│   └── eval_cases.yaml                 # LLM evaluation test cases
│
├── compose.yml                         # Docker Compose — PostgreSQL + Backend + Frontend
├── .env.example                        # Environment variable template (secrets excluded)
├── biome.json                          # Lint & format (Biome — fast, zero-config)
├── .gitignore
├── AGENTS.md                           # ← This file (source of truth)
├── CLAUDE.md                           # Symlink → AGENTS.md
├── .cursorrules                        # Symlink → AGENTS.md
├── .github/copilot-instructions.md     # Symlink → ../../AGENTS.md
├── session-progress.md                  # Lightweight session index (1-2 lines per task, points to `harness/workflows/runs/F-XXX/`)
├── feature_list.json                   # Atomic task backlog
├── init.sh                             # Environment initialization script
└── README.md                           # Challenge description (source document)
```

---

## 6. Feature List — Atomic Tasks

> This is the complete breakdown of the challenge into atomic, independently testable tasks.
> Stored in `feature_list.json` with the following schema:

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
  │ tasks    │     │ design   │     │ stubs        │     │ + tests          │
  └──────────┘     └──────────┘     └──────────────┘     └────────┬─────────┘
                                                                   │
                        ┌─────────────────────<────────────────────┘
                        ▼
              ┌──────────────────┐     ┌──────────────┐     ┌──────────────┐
              │  Code Reviewer   │────>│ Security Rev │────>│  DB Reviewer │
              │ reviews code +   │     │ audits sec   │     │ reviews schema│
              │ tests            │     │ concerns     │     │ + queries     │
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

Each task gets its **own handoff directory** under `harness/workflows/runs/F-XXX-task-name/`. This keeps context small — agents only read what's relevant.

### 7.2.1 Run Directory Structure

```
harness/workflows/runs/
├── F-001-campaign-crud/
│   ├── handoff.md       # Handoff FROM builder TO reviewer
│   ├── plan.md          # Tech Lead's pre-implementation plan
│   └── audit.log        # Raw command outputs, timestamps, errors
└── F-002-content-crud/
    └── ...
```

### 7.2.2 `session-progress.md` — Lightweight Index Only

`session-progress.md` is NOT a handoff dump. It is a **1-2 line summary per task** that points to the detailed handoff:

```markdown
## F-001 Campaign CRUD API — DONE
handoff → `harness/workflows/runs/F-001-campaign-crud/handoff.md`
reviewers: @code-reviewer ✅ @security-reviewer ✅

## F-002 Content Piece CRUD API — IN REVIEW
handoff → `harness/workflows/runs/F-002-content-crud/handoff.md`
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

## Not done / known issues
- Swagger UI not added (out of scope)

## Next actions
1. Code Reviewer: review `backend/campaign/`
2. Security Reviewer: verify env var handling

## Artifacts
- Migration: `backend/drizzle/0000_init/`
- Decision: `knowledge/decisions/001-campaign-soft-delete.md`
```

### 7.3 Error Recovery Protocol

When a task fails:

1. **Builder** logs the error in `knowledge/learnings/` with timestamp
2. **Builder** creates a new attempt in `feature_list.json` (bump `attempt` counter)
3. **Builder** logs the error in the task's `audit.log` under `harness/workflows/runs/F-XXX/`, and updates `session-progress.md` with "BLOCKED" status
4. **Tech Lead** reviews and may change the approach (new ADR if needed)
5. **Builder** retries with amended plan

---

## 8. Task Lifecycle & Done Criteria

### 8.1 Task States in `feature_list.json`

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
2. **All acceptance criteria** from `feature_list.json` pass
3. **Tests exist and pass** (unit + integration as specified)
4. **Code Reviewer approved** (no critical or major issues)
5. **Security Reviewer approved** (no exposed secrets, no injection vectors)
6. **Database Reviewer approved** (if DB schema changed — no N+1, proper indices)
7. **Manual verification** — task can be demonstrated via curl or UI
8. **Task run directory** created at `harness/workflows/runs/F-XXX/` with `handoff.md`, `plan.md`, `audit.log`
9. **`session-progress.md` updated** with 1-2 line summary pointing to the run directory
10. **`knowledge/decisions/` updated** if any design choice was made during implementation

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
| Unit (backend) | Jest / Vitest | `backend/test/unit/` | Services, validators, providers |
| Unit (frontend) | Vitest + React Testing Library | `frontend/src/**/*.test.tsx` | Components, hooks, utils |
| Integration | Supertest (NestJS) / TestClient (FastAPI) | `backend/test/e2e/` | Full endpoint request→response |
| AI Mock | jest.mock / unittest.mock | In unit test files | AI service with mocked provider |
| DB | Testcontainers / SQLite in-memory | `backend/test/e2e/` | Repository layer with real DB |

### 9.3 Test Pattern References

Full test examples are NOT inlined here. Instead, the skill `harness/skills/test-patterns.md` contains runnable examples for:

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

Minor decisions (not warranting a full ADR) are stored in `knowledge/decisions/`:

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

`knowledge/conventions/` documents team-wide coding standards. Created once, referenced by all agents.

Example — `knowledge/conventions/nestjs-structure.md`:

```markdown
# NestJS Module Structure Convention

Every feature module must contain:
- `*.controller.ts` — route handlers
- `*.service.ts` — business logic
- `*.module.ts` — module definition
- `dto/` — Data Transfer Objects with class-validator decorators
- `entities/` — TypeORM entities or Prisma schema references

Naming rules:
- Controller methods: `create()`, `findAll()`, `findOne()`, `update()`, `remove()`
- Service methods match controller names
- DTOs: `Create{Entity}Dto`, `Update{Entity}Dto`
- Always use validation pipes: `@Body(new ValidationPipe())`
```

### 11.2 Learnings Directory

When an agent encounters and resolves an error, they document it in `knowledge/learnings/` to prevent recurrence:

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
| H-001 | Which backend framework? | NestJS (TypeScript) / FastAPI (Python) / Fiber (Go) | Before Phase 0 |
| H-002 | Which AI provider(s)? | OpenAI only / Anthropic only / Both | Before Phase 1 |
| H-003 | Which React framework? | Vite / Next.js / Remix | Before Phase 4 |
| H-004 | API style? | REST only / GraphQL only / Both (REST for CRUD, GraphQL for real-time?) | During ADR-001 |
| H-005 | ORM / Query builder? | Prisma / TypeORM / Drizzle / Kysely / Raw SQL | Before F-003 |
| H-006 | Real-time library? | ws (WebSockets) / Socket.io / Server-Sent Events (native) / GraphQL Subscriptions | During ADR-003 |
| H-007 | Package manager? | pnpm / npm / yarn | Before Phase 0 |
| H-008 | Test runner? | Jest / Vitest | Before testing |

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
ln -sf ../../AGENTS.md .github/copilot-instructions.md
ln -sf AGENTS.md CLAUDE.md
ln -sf AGENTS.md .cursorrules
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

# Lint & format (Biome — runs on both backend and frontend)
pnpm biome check --write .

# Type check
cd backend && pnpm typecheck
cd frontend && pnpm typecheck

# Rebuild and restart Docker
docker compose down && docker compose up --build

# View PostgreSQL logs
docker compose logs -f db

# Connect to PostgreSQL
psql -h localhost -U postgres -d acme

# Open Swagger UI
open http://localhost:3000/api
```

### D. State Machine — Valid Transitions

```typescript
// ReviewState enum
enum ContentState {
  DRAFT = 'draft',
  SUGGESTED_BY_AI = 'suggested_by_ai',
  REVIEWED = 'reviewed',
  APPROVED = 'approved',
  REJECTED = 'rejected',
}

// Valid transitions map
const VALID_TRANSITIONS: Record<ContentState, ContentState[]> = {
  [ContentState.DRAFT]: [ContentState.SUGGESTED_BY_AI],
  [ContentState.SUGGESTED_BY_AI]: [ContentState.REVIEWED, ContentState.REJECTED],
  [ContentState.REVIEWED]: [ContentState.APPROVED, ContentState.REJECTED, ContentState.SUGGESTED_BY_AI],
  [ContentState.APPROVED]: [],
  [ContentState.REJECTED]: [ContentState.DRAFT, ContentState.SUGGESTED_BY_AI],
};
```

---

*This document is the single source of truth for all agents working on the ACME Content Workflow challenge. It is designed for ingestion into Google NotebookLM and use as system context for Claude, Cursor, Copilot, and other AI coding assistants.*
