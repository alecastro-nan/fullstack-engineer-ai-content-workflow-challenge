# Session Progress

Lightweight index for task execution. Each completed task gets a 1-2 line summary pointing to its detailed handoff directory.

---

## F-000 — Initialize monorepo — DONE
handoff → `harness/workflows/runs/F-000-init-monorepo/handoff.md`
reviewers: @code-reviewer ✅ @security-reviewer ✅

## F-001 — Campaign CRUD API — DONE
handoff → `harness/workflows/runs/F-001-campaign-crud/handoff.md`
reviewers: @code-reviewer ⏳ @security-reviewer ⏳

Notes: 10 unit + 10 e2e tests passing. SWC added to vitest configs for DI metadata support.

## F-002 — Content Piece CRUD API — PENDING
handoff → `harness/workflows/runs/F-002-content-crud/handoff.md`

## F-003 — PostgreSQL schema & migrations — PENDING
handoff → `harness/workflows/runs/F-003-db-schema/handoff.md`

## F-004 — AI provider abstraction layer — PENDING
handoff → `harness/workflows/runs/F-004-ai-abstraction/handoff.md`

## F-005 — AI draft generation endpoint — PENDING
handoff → `harness/workflows/runs/F-005-ai-draft/handoff.md`

## F-006 — AI translation/localization endpoint — PENDING
handoff → `harness/workflows/runs/F-006-ai-translation/handoff.md`

## F-007 — Review state machine — PENDING
handoff → `harness/workflows/runs/F-007-state-machine/handoff.md`

## F-008 — Review endpoints — PENDING
handoff → `harness/workflows/runs/F-008-review-endpoints/handoff.md`

## F-009 — WebSocket/SSE setup — PENDING
handoff → `harness/workflows/runs/F-009-realtime-setup/handoff.md`

## F-010 — Real-time broadcast — PENDING
handoff → `harness/workflows/runs/F-010-realtime-broadcast/handoff.md`

## F-011 — React project scaffold — PENDING
handoff → `harness/workflows/runs/F-011-react-scaffold/handoff.md`

## F-012 — Campaign Dashboard page — PENDING
handoff → `harness/workflows/runs/F-012-campaign-dashboard/handoff.md`

## F-013 — Campaign Detail page — PENDING
handoff → `harness/workflows/runs/F-013-campaign-detail/handoff.md`

## F-014 — AI Draft panel — PENDING
handoff → `harness/workflows/runs/F-014-ai-draft-panel/handoff.md`

## F-015 — Review UI — PENDING
handoff → `harness/workflows/runs/F-015-review-ui/handoff.md`

## F-016 — Translation panel — PENDING
handoff → `harness/workflows/runs/F-016-translation-panel/handoff.md`

## F-017 — Real-time status updates — PENDING
handoff → `harness/workflows/runs/F-017-realtime-frontend/handoff.md`

## F-018 — Docker Compose — PENDING
handoff → `harness/workflows/runs/F-018-docker-compose/handoff.md`

## F-019 — Dockerfiles — PENDING
handoff → `harness/workflows/runs/F-019-dockerfiles/handoff.md`

## F-020 — GitHub Actions CI — PENDING
handoff → `harness/workflows/runs/F-020-ci-pipeline/handoff.md`

## F-021 — E2E workflow test — PENDING
handoff → `harness/workflows/runs/F-021-e2e-test/handoff.md`

## F-022 — ADRs — PENDING
handoff → `harness/workflows/runs/F-022-adrs/handoff.md`

## F-023 — README update — PENDING
handoff → `harness/workflows/runs/F-023-readme/handoff.md`

## F-024 — Final smoke test and PR — PENDING
handoff → `harness/workflows/runs/F-024-final-pr/handoff.md`

---

## Security Audit: SkillSpector — DONE
7 critical/DO_NOT_INSTALL skills removed, `harness/skills/` deleted, lockfile + installer + AGENTS.md updated.
decision → `knowledge/decisions/002-remove-critical-skills.md`

## F-025 — Architecture replanning: NestJS→Django+Strawberry GraphQL — DONE
Full architecture migration from NestJS/TypeScript to Django (Python) + Strawberry GraphQL.
AGENTS.md, feature_list.json, conventions, install-skills.sh, skills-lock.json, ADRs all updated.
ADR-005 documents the Django+Strawberry decision.
decision → `docs/adrs/ADR-005-django-strawberry-architecture.md`
