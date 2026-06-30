# Decision: 2026-06-19 - Task Reordering with Smart Dependencies

## Context
The original task list had 21 pending tasks with suboptimal ordering:
- F-021 (Dockerfiles) was scheduled late (Phase 5) but the frontend Dockerfile is the single blocker for `docker compose up`
- F-009+F-010 (state machine + mutations) were separate but the state machine alone is untestable
- F-011+F-012 (WebSocket setup + broadcast) were separate but broadcast without setup is impossible
- F-013 (React scaffold) was a separate task but 80% of the scaffold already exists; the remaining wiring belongs in the Dashboard task
- No consideration for parallel execution

## Decision
Reorganize all pending tasks into 6 phases ordered by value delivery:

1. **Docker Sandbox** (F-006→F-007): Frontend Dockerfile + compose.yml finalization — unlocks `docker compose up`
2. **Backend Engine** (F-008→F-011): Review mutations + AI abstraction + AI draft + AI translation
3. **Frontend Core** (F-012→F-013): Dashboard + Detail pages
4. **Feature Panels** (F-014→F-016): AI Draft panel + Review UI + Translation panel
5. **Real-Time** (F-017→F-018): WebSocket setup + frontend integration
6. **Quality & Polish** (F-019→F-023): E2E test, ADRs, CI, README, final PR

### Merges
- Old F-009 (state machine) + F-010 (mutations) → **F-008** (one logical unit)
- Old F-011 (Channels setup) + F-012 (broadcast) → **F-017** (setup+broadcast)
- Old F-013 (scaffold) → absorbed into **F-012** (dashboard)

### Splits
- Old F-021 (Dockerfiles) → only frontend Dockerfile needed (backend one exists) → **F-006**

## Rationale
- Early Docker sandbox lets users run the full stack after just 2 tasks
- Backend Engine and Frontend Core can execute in parallel (zero shared dependencies)
- Merging test+gates pairs eliminates "untestable intermediate" states
- Reduces total pending tasks from 21 to 18 (3 merges, 0 net-new)

## Consequences
### Positive
- `docker compose up` works after F-006 + F-007 (previously after 7+ tasks)
- 5 parallel lanes at peak execution (F-006, F-008, F-009, F-012 can all start immediately)
- No orphan features (state machine always gets mutations, setup always gets broadcast)

### Negative
- Larger individual tasks (F-008, F-017) may take slightly longer per task
- Old task IDs no longer match original numbering

## References
- `agentic/tasks/feature_list.json` — updated with new ordering
- `agentic/tasks/session-progress.md` — updated with new task list
- `agentic/runs/F-replan-task-ordering/` — nanlabs-planner analysis
