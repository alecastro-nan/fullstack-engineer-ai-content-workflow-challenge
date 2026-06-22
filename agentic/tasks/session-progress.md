# Session Progress

Lightweight index for task execution. Each completed task gets a 1-2 line summary pointing to its detailed handoff directory.

---

## F-000 — Initialize monorepo — DONE
handoff → `agentic/runs/F-000-init-monorepo/handoff.md`
reviewers: @code-reviewer ✅ @security-reviewer ✅

## F-001 — Clean up old NestJS/TypeScript backend artifacts — DONE
handoff → `agentic/runs/F-001-cleanup-backend/handoff.md`
reviewers: @code-reviewer ✅ @security-reviewer ✅

## Architecture Fixes — Integration Readiness — DONE
handoff → `docs/architecture-review.md`
Fixes applied: CORS config, Dockerfile ASGI, compose.yml ports+frontend, ADR-004 completed, init.sh rewrite, Vite proxy fix, F-001/F-005 cleanup in feature_list

## F-002 — Install Django + Strawberry GraphQL + Python backend stack — DONE
handoff → `agentic/runs/F-002-install-django-stack/handoff.md`
reviewers: @code-reviewer ✅ @security-reviewer ✅
Fixes applied: secrets moved to env_file, security headers added, SECRET_KEY guard, dev deps consolidated

## F-003 — Campaign CRUD GraphQL API — DONE
handoff → `agentic/runs/F-003-campaign-crud/handoff.md`
reviewers: @code-reviewer ✅ @security-reviewer ✅ @database-reviewer ✅

## F-004 — Content Piece CRUD GraphQL API — DONE
handoff → `agentic/runs/F-004-content-crud/handoff.md`
plan → `agentic/runs/F-004-content-crud/plan.md`
reviewers: @code-reviewer ✅ @security-reviewer ✅ @database-reviewer ✅

## F-005 — PostgreSQL schema & Django migrations — DONE
handoff → `agentic/runs/F-005-db-schema/handoff.md`
reviewers: @code-reviewer ✅ @security-reviewer ✅ @database-reviewer ✅
*Completed as part of F-003 and F-004. Migrations: campaigns 0001, content 0001 + 0002.*

## Phase 1: Docker Sandbox (unblocks `docker compose up`)

### F-006 — Frontend Dockerfile — DONE
handoff → `agentic/runs/F-006-frontend-dockerfile/handoff.md`
reviewers: @code-reviewer ✅ @security-reviewer ⏳ (critical: nginx.conf removed from .dockerignore, fixed inline)
*Multi-stage builder (node:20-alpine) + production (nginx:alpine), nginx.conf with proxy to backend, .dockerignore. Fix applied: removed nginx.conf from .dockerignore (was breaking Docker build).*

### F-007 — Finalize Docker Compose — DONE
handoff → `agentic/runs/F-007-finalize-compose/handoff.md`
reviewers: @code-reviewer ✅ @security-reviewer ✅
*Healthchecks, restart policies, build args for VITE_API_URL, api.ts fallback fix, env.example ports fixed. Both reviews passed with production-hardening notes.*

## Phase 2 Plan Registered
plan → `agentic/runs/phase-2-plan/plan.md`
*15 remaining tasks across 4 parallel tracks. Estimated ~11.5h total.*

## Phase 2: Backend Engine (parallelizable)

### F-008 — Review state machine + mutations (merged) — DONE
handoff → `agentic/runs/F-008-review-state-machine-mutations/handoff.md`
reviewers: @code-reviewer ✅ @security-reviewer ✅ @database-reviewer ✅
*Merged old F-009+F-010. State machine guards + GraphQL review mutations. Review found and fixed: VALID_TRANSITIONS restored, self-import removed, edit_content double-save/TOCTOU bug fixed, EDIT enum added, feedback max_length, on_delete=CASCADE→PROTECT. 32 tests, mypy+ruff clean.*

### F-009 — AI provider abstraction layer — PENDING
handoff → `agentic/runs/F-009-ai-abstraction/handoff.md`
*Can run in parallel with F-008. OpenAI + Anthropic SDK wrappers with fallback.*

### F-010 — AI draft generation mutation — PENDING
handoff → `agentic/runs/F-010-ai-draft/handoff.md`
*Depends on F-009. Can run in parallel with F-011.*

### F-011 — AI translation mutation — PENDING
handoff → `agentic/runs/F-011-ai-translation/handoff.md`
*Depends on F-009. Can run in parallel with F-010.*

## Phase 3: Frontend Core (parallel with Phase 2)

### F-012 — Campaign Dashboard (absorbs scaffold) — PENDING
handoff → `agentic/runs/F-012-campaign-dashboard/handoff.md`
*Absorbed old F-013. Routes, API client wiring, campaign list + create page.*

### F-013 — Campaign Detail page — PENDING
handoff → `agentic/runs/F-013-campaign-detail/handoff.md`
*Depends on F-012. Content pieces list, state badges, create content.*

## Phase 4: Feature Panels (after Phase 2+3)

### F-014 — AI Draft panel — PENDING
handoff → `agentic/runs/F-014-ai-draft-panel/handoff.md`
*Depends on F-010 + F-013. Trigger generation, preview, accept/reject.*

### F-015 — Review UI — PENDING
handoff → `agentic/runs/F-015-review-ui/handoff.md`
*Depends on F-008 + F-013. Approve/reject/request edits buttons.*

### F-016 — Translation panel — PENDING
handoff → `agentic/runs/F-016-translation-panel/handoff.md`
*Depends on F-011 + F-013. Language selector, trigger, preview.*

## Phase 5: Real-Time

### F-017 — Channels WebSocket + broadcasts (merged) — PENDING
handoff → `agentic/runs/F-017-channels-websocket/handoff.md`
*Merged old F-011+F-012. Django Channels setup + state change broadcasts.*

### F-018 — Frontend real-time updates — PENDING
handoff → `agentic/runs/F-018-frontend-realtime/handoff.md`
*Depends on F-017 + F-013. WebSocket client, auto-refresh, toasts.*

## Phase 6: Quality & Polish

### F-019 — End-to-end workflow test — PENDING
handoff → `agentic/runs/F-019-e2e-test/handoff.md`
*Depends on F-010 + F-008 + F-011 + F-017. Full Campaign→Content→AI→Review→Translation test.*

### F-020 — Complete pending ADRs — PENDING
handoff → `agentic/runs/F-020-adrs/handoff.md`
*Depends on F-009 + F-017. Complete ADR-002 (AI provider) + ADR-003 (real-time).*

### F-021 — GitHub Actions CI — PENDING
handoff → `agentic/runs/F-021-ci-pipeline/handoff.md`
*Depends on F-007. Ruff, mypy, pytest, vitest, Docker build checks.*

### F-022 — README update — PENDING
handoff → `agentic/runs/F-022-readme/handoff.md`
*Final comprehensive README with setup, decisions, API reference, architecture.*

### F-023 — Final smoke test + PR — PENDING
handoff → `agentic/runs/F-023-final-pr/handoff.md`
*Depends on F-019 + F-020 + F-021 + F-022. docker compose up verify + PR creation.*

---

## Security Audit: SkillSpector — DONE
7 critical/DO_NOT_INSTALL skills removed, `harness/skills/` deleted, lockfile + installer + AGENTS.md updated.
decision → `agentic/knowledge/decisions/002-remove-critical-skills.md`

## F-027 — Architecture replanning: NestJS→Django+Strawberry GraphQL — DONE
Full architecture migration from NestJS/TypeScript to Django (Python) + Strawberry GraphQL.
AGENTS.md, feature_list.json, conventions, install-skills.sh, skills-lock.json, ADRs all updated.
ADR-005 documents the Django+Strawberry decision.
decision → `docs/adrs/ADR-005-django-strawberry-architecture.md`
