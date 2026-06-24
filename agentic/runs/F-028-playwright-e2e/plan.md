# Plan — F-028: Comprehensive Playwright E2E Test

## Objective
Write an exhaustive Playwright test suite that validates the entire ACME Content Workflow from a real browser, covering every user-facing feature and all recently applied infrastructure fixes.

## Approach

### Tooling
- **Playwright** (already listed in AGENTS.md as the E2E tool, used via `@nanlabs-e2e-runner`)
- Add `@playwright/test` as a devDependency in `frontend/package.json`
- Playwright config at `frontend/playwright.config.ts` targeting `http://localhost:5173`
- Tests live at `frontend/tests/e2e/workflow.spec.ts`

### AI Mocking Strategy
Intercept `/graphql` requests at the Playwright route level for AI mutations:
- `generateDraft` → return mock drafted content
- `translateContent` → return mock translated content
This avoids requiring real API keys in E2E tests.

### Test Isolation
- Each test creates its own campaign/content with unique names (timestamp-based)
- Tests are ordered to build on each other (create → use → verify), no shared state cleanup needed beyond unique naming
- AI mutations use Playwright `page.route()` interception

### Environment
- Tests run against `docker compose up` (db + backend + frontend)
- Backend must be healthy before tests start (wait-for pattern)
- Test script: `pnpm test:e2e` in frontend/package.json

### Test Map (order matters for state progression)

```
1. healthChecks.spec.ts
   └── Docker containers running, GraphQL responds, Frontend serves

2. campaigns.spec.ts
   └── Dashboard loads → Create → List → Navigate → Delete

3. contentPieces.spec.ts
   └── Add content → Edit → State badge renders

4. aiDraft.spec.ts
   └── Generate → State changes → Badge updates

5. reviewWorkflow.spec.ts
   └── Approve → Reject → Request edits → Edit & reset

6. translation.spec.ts
   └── Translate approved content → Verify new piece

7. realtime.spec.ts
   └── WebSocket connects → State changes broadcast

8. regression.spec.ts
   └── CSRF, enum case, nginx, health checks, collectstatic, uv.lock
```

## Files to Create/Modify

| File | Action |
|---|---|
| `frontend/playwright.config.ts` | Create — Playwright config for Chromium, baseURL, timeouts |
| `frontend/tests/e2e/workflow.spec.ts` | Create — Main test file (all scenarios) |
| `frontend/package.json` | Modify — Add @playwright/test, add test:e2e script |
| `frontend/tsconfig.json` | Modify — Add e2e test paths if needed |
| `README.md` | Modify — Add E2E test section |

## Bug / Blocker Reporting

The test suite includes a post-run hook that generates `agentic/runs/F-028-playwright-e2e/bug-report.md`:

### bug-report.md Structure
```markdown
# Bug Report — F-028 Playwright E2E Suite
**Date:** 2026-06-24
**Run ID:** <timestamp>
**Passed:** 42 / 45
**Failed:** 3

## Failed Tests

### 1. Create Campaign validation rejects empty name
- **Test:** `campaigns > create > rejects empty name`
- **Error:** `TimeoutError: locator.waitFor: Timeout 5000ms exceeded`
- **Root Cause:** Validation error toast has wrong CSS selector in test
- **Severity:** major
- **Proposed Fix:** Update selector from `.toast-error` to `[data-testid="error-toast"]`
- **Proposed Task:** F-029 — Fix campaign validation E2E selector mismatch

### 2. AI draft mutation returns 500
- **Test:** `aiDraft > generate > success path`
- **Error:** `GraphQL response: {"errors":[{"message":"OPENAI_API_KEY not configured"}]}`
- **Root Cause:** AI route interception not matching the mutation — real API call attempted
- **Severity:** blocker
- **Proposed Fix:** Fix Playwright route pattern to match `generateDraft` mutation operation name
- **Proposed Task:** F-030 — Fix AI mutation route interception in E2E tests

### 3. ...etc

## Summary
- **Blockers:** 1 (AI route interception)
- **Major:** 1 (CSS selector)
- **Minor:** 1 (flaky WebSocket reconnect timing)
- **Next:** Create tasks F-029, F-030, F-031 in feature_list.json
```

### How It Works
- Playwright's `test.afterEach` and `test.afterAll` hooks collect failure details
- On suite completion, a script aggregates all failures into `bug-report.md`
- The report proposes new task IDs sequentially from the highest existing ID
- If all tests pass, report states `0 bugs found` and no new tasks are created

## Verification
```bash
docker compose up -d  # ensure all services running
cd frontend
pnpm playwright install chromium
pnpm test:e2e          # runs all E2E tests

# Check bug report if failures occurred
cat ../agentic/runs/F-028-playwright-e2e/bug-report.md
```

All ~45 acceptance criteria must pass, OR bug-report.md must accurately document every failure with root cause and proposed task.
