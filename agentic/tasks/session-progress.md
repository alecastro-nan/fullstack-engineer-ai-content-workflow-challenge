# Session Progress

Lightweight index for task execution. Each completed task gets a 1-2 line summary pointing to its detailed handoff directory.

---

## F-000 — Initialize monorepo — DONE
handoff → `agentic/runs/F-000-init-monorepo/handoff.md`
reviewers: @code-reviewer ✅ @security-reviewer ✅

## F-001 — Clean up old NestJS/TypeScript backend artifacts — DONE
handoff → `agentic/runs/F-001-cleanup-backend/handoff.md`
reviewers: @code-reviewer ⏳ @security-reviewer ⏳

## F-002 — Install Django + Strawberry GraphQL + Python backend stack — PENDING
handoff → `agentic/runs/F-002-install-django-stack/handoff.md`

## F-003 — Campaign CRUD GraphQL API — PENDING
handoff → `agentic/runs/F-003-campaign-crud/handoff.md`

## F-004 — Content Piece CRUD GraphQL API — PENDING
handoff → `agentic/runs/F-004-content-crud/handoff.md`

## F-005 — PostgreSQL schema & Django migrations — PENDING
handoff → `agentic/runs/F-005-db-schema/handoff.md`

## F-006 — AI provider abstraction layer — PENDING
handoff → `agentic/runs/F-006-ai-abstraction/handoff.md`

## F-007 — AI draft generation GraphQL mutation — PENDING
handoff → `agentic/runs/F-007-ai-draft/handoff.md`

## F-008 — AI translation/localization GraphQL mutation — PENDING
handoff → `agentic/runs/F-008-ai-translation/handoff.md`

## F-009 — Review state machine — PENDING
handoff → `agentic/runs/F-009-state-machine/handoff.md`

## F-010 — Review GraphQL mutations — PENDING
handoff → `agentic/runs/F-010-review-mutations/handoff.md`

## F-011 — WebSocket/SSE setup in Django — PENDING
handoff → `agentic/runs/F-011-realtime-setup/handoff.md`

## F-012 — Real-time broadcast on state changes — PENDING
handoff → `agentic/runs/F-012-realtime-broadcast/handoff.md`

## F-013 — React project scaffold — PENDING
handoff → `agentic/runs/F-013-react-scaffold/handoff.md`

## F-014 — Campaign Dashboard page — PENDING
handoff → `agentic/runs/F-014-campaign-dashboard/handoff.md`

## F-015 — Campaign Detail page — PENDING
handoff → `agentic/runs/F-015-campaign-detail/handoff.md`

## F-016 — AI Draft panel — PENDING
handoff → `agentic/runs/F-016-ai-draft-panel/handoff.md`

## F-017 — Review UI — PENDING
handoff → `agentic/runs/F-017-review-ui/handoff.md`

## F-018 — Translation panel — PENDING
handoff → `agentic/runs/F-018-translation-panel/handoff.md`

## F-019 — Real-time status updates on frontend — PENDING
handoff → `agentic/runs/F-019-realtime-frontend/handoff.md`

## F-020 — Docker Compose — PENDING
handoff → `agentic/runs/F-020-docker-compose/handoff.md`

## F-021 — Dockerfiles — PENDING
handoff → `agentic/runs/F-021-dockerfiles/handoff.md`

## F-022 — GitHub Actions CI — PENDING
handoff → `agentic/runs/F-022-ci-pipeline/handoff.md`

## F-023 — E2E workflow test — PENDING
handoff → `agentic/runs/F-023-e2e-test/handoff.md`

## F-024 — ADRs — PENDING
handoff → `agentic/runs/F-024-adrs/handoff.md`

## F-025 — README update — PENDING
handoff → `agentic/runs/F-025-readme/handoff.md`

## F-026 — Final smoke test and PR — PENDING
handoff → `agentic/runs/F-026-final-pr/handoff.md`

---

## Security Audit: SkillSpector — DONE
7 critical/DO_NOT_INSTALL skills removed, `harness/skills/` deleted, lockfile + installer + AGENTS.md updated.
decision → `agentic/knowledge/decisions/002-remove-critical-skills.md`

## F-027 — Architecture replanning: NestJS→Django+Strawberry GraphQL — DONE
Full architecture migration from NestJS/TypeScript to Django (Python) + Strawberry GraphQL.
AGENTS.md, feature_list.json, conventions, install-skills.sh, skills-lock.json, ADRs all updated.
ADR-005 documents the Django+Strawberry decision.
decision → `docs/adrs/ADR-005-django-strawberry-architecture.md`
