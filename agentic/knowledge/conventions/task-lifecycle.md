# Task Lifecycle — Standard Workflow for Feature Tasks

Every feature task (F-XXX) follows this lifecycle. Agents MUST follow this flow
for every task — it is not optional.

## Lifecycle Diagram

```
  ╔══════════════════════════════════════════════════════════════╗
  ║                    TASK LIFECYCLE                           ║
  ╚══════════════════════════════════════════════════════════════╝

  1. PLAN
     │
     ├── Read feature_list.json for acceptance criteria
     ├── Create harness/workflows/runs/F-XXX/plan.md
     └── (optional) @nanlabs-planner for complex tasks
     │
     ▼
  2. IMPLEMENT
     │
     ├── Write code in correct directories
     ├── Write tests alongside code
     ├── Make atomic commits (conventional commits)
     ├── Verify: build, typecheck, test all pass
     └── Update handoff.md and session-progress.md
     │
     ▼
  3. REVIEW (FIX → REVIEW loop)
     │
     ├── Call @code-reviewer via Task tool
     │   ├── If CHANGES REQUESTED → fix issues → go to step 4
     │   └── If APPROVED → continue
     │
     ├── Call @security-reviewer via Task tool
     │   ├── If CHANGES REQUIRED → fix issues → go to step 4
     │   └── If APPROVED → continue
     │
     └── Call @database-reviewer (if DB schema changed)
     │
     ▼
  4. FIX
     │
     ├── Address ALL issues from reviewers
     ├── Make atomic commits per fix category
     ├── Verify: build, typecheck, test still pass
     └── Return to step 3 (REVIEW) for re-check
     │
     ▼
  5. FINALIZE (only after ALL reviewers APPROVED)
     │
     ├── Update feature_list.json: status → "done"
     ├── Update session-progress.md: reviewers ✅
     ├── Update handoff.md with final state
     └── Proceed to next task
```

## Detailed Steps

### Step 1: Plan
- Read `feature_list.json` for the task's acceptance criteria and test requirements
- Create directory: `harness/workflows/runs/F-XXX-task-name/`
- Create `plan.md` with ordered implementation steps, file list, verification commands
- For complex tasks, delegate to @nanlabs-planner first

### Step 2: Implement
- Write production code AND tests
- Follow the folder structure from AGENTS.md section 5
- Make atomic commits with conventional commit format:
  `type(scope): message`
  Types: feat, fix, refactor, test, docs, chore, infra, style
- After implementation, verify:
  ```bash
  pnpm build        # or nest build / vite build
  pnpm typecheck    # or tsc --noEmit
  pnpm test         # or vitest run
  pnpm lint:ci      # or biome check
  ```
- Create `handoff.md` with what was done, not done, and next actions

### Step 3: Review (FIX → REVIEW loop)
Use the Task tool to invoke each reviewer:

```bash
# Invoke code reviewer
task "review F-XXX" subagent_type=nanlabs-code-reviewer

# Invoke security reviewer
task "review F-XXX" subagent_type=nanlabs-security-reviewer

# Invoke database reviewer (only if DB schema changed)
task "review F-XXX schema" subagent_type=nanlabs-database-reviewer
```

Reviewers will produce a report with one of these outcomes:
- **APPROVED** — no changes needed, proceed to finalize
- **CHANGES REQUESTED** (critical/major) — must fix before merge
- **CHANGES REQUIRED** (minor) — should fix before final sign-off

### Step 4: Fix
- Address ALL issues from reviewers
- Fix critical/major issues first, then warnings, then suggestions
- Make atomic commits (one commit per fix category)
- Re-verify build, typecheck, test, lint after fixes
- Commit fixes and call reviewers again for re-review
- Repeat until both reviewers APPROVE

### Step 5: Finalize
Once ALL reviewers have approved:
1. Update `feature_list.json`: set `status` to `"done"`
2. Update `session-progress.md`: change `⏳` to `✅` for all reviewers
3. Update `handoff.md` with final notes
4. Commit these changes

## Commit Strategy

Each task should produce multiple atomic commits:

```
# Implementation commits
feat(scope): implement feature X
test(scope): add tests for feature X

# Fix commits (from review feedback)
fix(scope): address code review: [specific issue]
fix(scope): address security review: [specific issue]

# Finalization
chore(handoff): mark F-XXX as DONE and update session-progress
```

## Verification Before Each Review Invocation

Before calling ANY reviewer, run the full verification suite:

```bash
cd backend && pnpm build && pnpm typecheck && pnpm test
cd frontend && pnpm build && pnpm typecheck
cd / && pnpm lint:ci
```

If any of these fail, fix the issue FIRST before calling the reviewer.
A reviewer invocation with failing CI is wasted effort.
