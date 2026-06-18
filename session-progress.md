# Session Progress

Lightweight index for task execution. Each completed task gets a 1-2 line summary pointing to its detailed handoff directory.

---

## F-000 — Initialize monorepo — DONE
handoff → `harness/workflows/runs/F-000-init-monorepo/handoff.md`
reviewers: @code-reviewer ✅ @security-reviewer ✅

## F-001 — Clean up old NestJS/TypeScript backend artifacts — PENDING
handoff → `harness/workflows/runs/F-001-cleanup-backend/handoff.md`

## F-002 — Campaign CRUD GraphQL API — PENDING
handoff → `harness/workflows/runs/F-002-campaign-crud/handoff.md`

## F-003 — Content Piece CRUD GraphQL API — PENDING
handoff → `harness/workflows/runs/F-003-content-crud/handoff.md`

## F-004 — PostgreSQL schema & Django migrations — PENDING
handoff → `harness/workflows/runs/F-004-db-schema/handoff.md`

## F-005 — AI provider abstraction layer — PENDING
handoff → `harness/workflows/runs/F-005-ai-abstraction/handoff.md`

## F-006 — AI draft generation GraphQL mutation — PENDING
handoff → `harness/workflows/runs/F-006-ai-draft/handoff.md`

## F-007 — AI translation/localization GraphQL mutation — PENDING
handoff → `harness/workflows/runs/F-007-ai-translation/handoff.md`

## F-008 — Review state machine — PENDING
handoff → `harness/workflows/runs/F-008-state-machine/handoff.md`

## F-009 — Review GraphQL mutations — PENDING
handoff → `harness/workflows/runs/F-009-review-mutations/handoff.md`

## F-010 — WebSocket/SSE setup in Django — PENDING
handoff → `harness/workflows/runs/F-010-realtime-setup/handoff.md`

## F-011 — Real-time broadcast on state changes — PENDING
handoff → `harness/workflows/runs/F-011-realtime-broadcast/handoff.md`

## F-012 — React project scaffold — PENDING
handoff → `harness/workflows/runs/F-012-react-scaffold/handoff.md`

## F-013 — Campaign Dashboard page — PENDING
handoff → `harness/workflows/runs/F-013-campaign-dashboard/handoff.md`

## F-014 — Campaign Detail page — PENDING
handoff → `harness/workflows/runs/F-014-campaign-detail/handoff.md`

## F-015 — AI Draft panel — PENDING
handoff → `harness/workflows/runs/F-015-ai-draft-panel/handoff.md`

## F-016 — Review UI — PENDING
handoff → `harness/workflows/runs/F-016-review-ui/handoff.md`

## F-017 — Translation panel — PENDING
handoff → `harness/workflows/runs/F-017-translation-panel/handoff.md`

## F-018 — Real-time status updates on frontend — PENDING
handoff → `harness/workflows/runs/F-018-realtime-frontend/handoff.md`

## F-019 — Docker Compose — PENDING
handoff → `harness/workflows/runs/F-019-docker-compose/handoff.md`

## F-020 — Dockerfiles — PENDING
handoff → `harness/workflows/runs/F-020-dockerfiles/handoff.md`

## F-021 — GitHub Actions CI — PENDING
handoff → `harness/workflows/runs/F-021-ci-pipeline/handoff.md`

## F-022 — E2E workflow test — PENDING
handoff → `harness/workflows/runs/F-022-e2e-test/handoff.md`

## F-023 — ADRs — PENDING
handoff → `harness/workflows/runs/F-023-adrs/handoff.md`

## F-024 — README update — PENDING
handoff → `harness/workflows/runs/F-024-readme/handoff.md`

## F-025 — Final smoke test and PR — PENDING
handoff → `harness/workflows/runs/F-025-final-pr/handoff.md`

---

## Security Audit: SkillSpector — DONE
7 critical/DO_NOT_INSTALL skills removed, `harness/skills/` deleted, lockfile + installer + AGENTS.md updated.
decision → `knowledge/decisions/002-remove-critical-skills.md`

## F-026 — Architecture replanning: NestJS→Django+Strawberry GraphQL — DONE
Full architecture migration from NestJS/TypeScript to Django (Python) + Strawberry GraphQL.
AGENTS.md, feature_list.json, conventions, install-skills.sh, skills-lock.json, ADRs all updated.
ADR-005 documents the Django+Strawberry decision.
decision → `docs/adrs/ADR-005-django-strawberry-architecture.md`
