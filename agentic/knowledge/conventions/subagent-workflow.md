# Subagent Workflow Convention

## Purpose
Defines which NaNLABS subagents to invoke during task execution and in what order, based on task type, stack, and quality gate requirements.

## Reference
AGENTS.md section 7.4 contains the high-level strategy. This file provides the detailed definitions for each active subagent.

---

## Active Subagents

### @nanlabs-planner
- **When**: Start of complex tasks (>45min estimated) or new development phases
- **Trigger**: Before F-006 (AI abstraction), F-011 (Channels), F-013 (frontend scaffold)
- **Output**: Task breakdown with atomic steps, risk assessment, dependency order
- **Verification**: Planner produces a plan.md in the task's run directory

### @nanlabs-tdd-guide
- **When**: Before implementing any backend feature
- **Trigger**: Before F-003, F-004, F-006, F-007, F-008, F-009, F-010
- **Output**: Test stubs following AAA pattern (Arrange, Act, Assert)
- **Verification**: Tests exist in `backend/apps/<app>/tests/` before implementation
- **Rules**: Mock all AI providers (R-009), test success + error paths (R-008)

### @nanlabs-code-reviewer
- **When**: After every backend or frontend feature task
- **Trigger**: After Builder completes code + tests
- **Output**: Review findings in `agentic/runs/F-XXX/review.md`
- **Verification**: No critical or major issues; ruff + mypy + pytest pass
- **Rules**: R-017 (mandatory gate), cannot skip before moving to next task

### @nanlabs-security-reviewer
- **When**: After code review passes, for any task touching API keys, user input, or data
- **Trigger**: After @code-reviewer approves
- **Output**: Security findings in `agentic/runs/F-XXX/security-review.md`
- **Verification**: R-007 (no hardcoded secrets), R-012 (explicit error handling)
- **Rules**: Blocks promotion if any critical/high finding is unresolved

### @nanlabs-database-reviewer
- **When**: During tasks that create or modify database schema
- **Trigger**: F-003 (Campaign model), F-004 (ContentPiece model), F-009 (state machine)
- **Output**: Schema review in `agentic/runs/F-XXX/db-review.md`
- **Verification**: Normalization, indices, FK constraints, N+1 prevention, migration idempotency

### @nanlabs-typescript-reviewer
- **When**: After every frontend feature task
- **Trigger**: After Builder implements frontend code (F-013 through F-019)
- **Output**: TypeScript review in `agentic/runs/F-XXX/ts-review.md`
- **Verification**: No `any` types, proper generics, strict mode compliance

### @nanlabs-e2e-runner
- **When**: During F-023 (end-to-end workflow test)
- **Trigger**: When all features are implemented and need integration verification
- **Output**: Playwright E2E test file + run results
- **Verification**: Full Campaign -> Content -> AI Draft -> Review -> Translation workflow passes

---

## Inactive Subagents (not used)

| Subagent | Rationale |
|---|---|
| `@nanlabs-performance-optimizer` | No performance benchmarks or SLAs in scope |
| `@nanlabs-refactor-cleaner` | Greenfield code — no tech debt |
| `@nanlabs-tech-assistant` | NaNLABS internal ops, not challenge-relevant |
| `@nanlabs-client-workflow-bootstrap` | Workflow already configured |
| `@nanlabs-reference-lookup` | AGENTS.md is single source of truth |
| `@nanlabs-docs-lookup` | Direct docs access is faster |
| `@nanlabs-build-error-resolver` | Reactive only (if build fails) |
| `@nanlabs-assistant` | Redundant — AGENTS.md provides full context |
| `@nanlabs-architect` | Invoked once per phase, not per-task |

---

## Task Execution Templates

### Backend Feature
```
1. @planner(?)       → Break down task into atomic steps (optional)
2. @tdd-guide        → Write test stubs
3. Builder           → Implement code + make tests pass
4. @database-reviewer → Review schema (if DB changes)
5. @code-reviewer    → Review code + tests
6. @security-reviewer → Audit for secrets, injection, validation
7. Mark done in feature_list.json + session-progress.md
```

### Frontend Feature
```
1. @planner(?)       → Break down component hierarchy (optional)
2. Builder           → Implement components + hooks + services
3. @typescript-reviewer → Review type safety
4. @code-reviewer    → Review code + tests
5. Mark done
```

### Infrastructure
```
1. Builder           → Implement Docker/compose/CI changes
2. @code-reviewer    → Review
3. @security-reviewer → Audit (Docker non-root, secrets, ports)
4. Mark done
```

### E2E / Quality
```
1. @e2e-runner       → Write Playwright test
2. @code-reviewer    → Review
3. Mark done
```
