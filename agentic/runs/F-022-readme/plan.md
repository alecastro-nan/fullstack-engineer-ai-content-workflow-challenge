# Plan — F-022: README update

## Current state analysis

The README is partially out of date — it still lists AI provider abstraction, frontend Dockerfile, AI draft generation, translation, real-time, and frontend as "In Progress" or "Planned", but all are implemented.

**What's already good:**
- CI badge, tech stack table, architecture diagram, GraphQL API examples, project structure, CI pipeline docs, how-to-run

**What needs updating:**
1. **Current Status** section — rewrite to reflect final state (everything is done)
2. **Prerequisites** — dedicated section with versions (currently buried in How to Run)
3. **Tech stack with ADR links** — add references to docs/adrs/ADR-00x.md for each decision
4. **AI draft generation mutation** (`generateDraft`) — missing from GraphQL reference
5. **AI translation mutation** (`translateContent`) — missing from GraphQL reference
6. **WebSocket / real-time docs** — missing entirely (URL pattern, message format)
7. **Available scripts** — not documented (test, lint, typecheck, dev)
8. **Environment variables** — not documented (reference table for all env vars)
9. **Project structure** — expand to show `backend/apps/` and `frontend/src/` hierarchy
10. **Links to ADRs** — add inline links in tech stack and dedicated docs section

## Implementation approach

Comprehensive rewrite of README.md addressing all acceptance criteria. Keep existing content that's still current; rewrite outdated sections; add missing sections.

## Files modified
- `README.md`: full rewrite
- `agentic/tasks/feature_list.json`: F-022 → done
- `agentic/tasks/session-progress.md`: F-022 → DONE
- `agentic/runs/F-022-readme/plan.md`: this file
