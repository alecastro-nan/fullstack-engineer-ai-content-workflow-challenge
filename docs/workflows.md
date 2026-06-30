# ACME Content Workflow — Development Workflow

> **For humans.** This document explains the agent-assisted development workflow used in this project.

## Overview

This project uses a structured agentic workflow where AI subagents with specialized roles execute tasks in a defined sequence. Each task goes through a pipeline of quality gates before being marked complete.

## Subagent Roles (7 Active)

| Role | What It Does | When |
|---|---|---|
| **Planner** (`@nanlabs-planner`) | Breaks complex tasks into atomic steps with risk assessment | Start of complex tasks or new phases |
| **TDD Guide** (`@nanlabs-tdd-guide`) | Writes test stubs before any implementation code | Before every backend feature |
| **Builder** (main agent) | Implements code, runs tests, commits changes | Every task |
| **Database Reviewer** (`@nanlabs-database-reviewer`) | Reviews schema design, indices, migrations | When DB schema changes |
| **TypeScript Reviewer** (`@nanlabs-typescript-reviewer`) | Reviews type safety for frontend code | After every frontend task |
| **Code Reviewer** (`@nanlabs-code-reviewer`) | Reviews all code for correctness, style, quality | After every task (mandatory gate) |
| **Security Reviewer** (`@nanlabs-security-reviewer`) | Audits for hardcoded secrets, injection, validation | After code review passes |
| **E2E Runner** (`@nanlabs-e2e-runner`) | Writes and runs Playwright end-to-end tests | Final integration phase |

## Task Lifecycle

```
Pending → In Progress → Review → Security Review → Done
                                      ↓ (if issues)
                                   Rework → Review
```

Each task produces:
- Code in the correct directory
- Tests (unit + integration)
- A run directory at `agentic/runs/F-XXX/` with handoff, plan, and audit logs
- An entry in `agentic/tasks/session-progress.md`

## Quality Gates

Every task must pass these before being marked done:

| Gate | What's Checked | Enforced By |
|---|---|---|
| Tests pass | pytest (backend) or Vitest (frontend) | Code Reviewer |
| Type checking | mypy strict mode (Python) or TypeScript strict | Code Reviewer |
| Linting | ruff (Python) or Biome (frontend) | Code Reviewer |
| No hardcoded secrets | API keys, DB passwords only via env vars | Security Reviewer |
| Every endpoint has a test | At least one unit test per endpoint | TDD Guide + Code Reviewer |
| AI calls are mocked | No real OpenAI/Anthropic API calls in unit tests | TDD Guide + Code Reviewer |

## Subagents Not Used

These were evaluated and intentionally excluded for this project:
- **Performance Optimizer**: No performance requirements in scope
- **Refactor Cleaner**: All code is greenfield (new development)
- **Reference Lookup**: AGENTS.md is the single source of truth
- **Docs Lookup**: Framework docs are directly accessible
- **Build Error Resolver**: Only invoked reactively if a build fails

## Branch & PR Workflow

1. Create branch: `feat/<task-id>-<description>`
2. Execute task through all quality gates
3. Commit with conventional commits: `type(scope): message`
4. Push and create PR against `feat/agentic-plan`
5. PR uses `.github/PULL_REQUEST_TEMPLATE.md`

## Reference
- Full agent workflow: `agentic/AGENTS.md` section 7
- Subagent conventions: `agentic/knowledge/conventions/subagent-workflow.md`
- Task backlog: `agentic/tasks/feature_list.json`
- Progress: `agentic/tasks/session-progress.md`
