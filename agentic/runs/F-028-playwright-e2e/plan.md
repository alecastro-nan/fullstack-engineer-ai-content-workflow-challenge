# Plan — F-028: Comprehensive Playwright E2E Test

## Current State

Existing E2E suite at `frontend/tests/e2e/` has:
- **workflow.spec.ts** (421 lines, 33 tests across 9 describe blocks)
- **helpers.ts** (194 lines — GraphQL stubs, route handlers, CRUD helpers)
- **bug-reporter.ts** (132 lines — custom Playwright reporter, auto-generates bug-report.md)
- **global-setup.ts** (88 lines — waits for frontend + GraphQL, cleans DB)
- **playwright.config.ts** (34 lines — chromium, 1 worker, 30s timeout, JSON + bug reporter)

**Last run:** All 33 tests passed (0 failures). Bug reporter generates at `agentic/runs/F-028-playwright-e2e/bug-report.md`.

---

## Gaps vs Feature List (45+ acceptance criteria)

| Category | Existing | Missing |
|---|---|---|
| Infrastructure | Frontend 200, GraphQL health | Docker container health check (all 3 running), Backend 200 |
| Campaigns | Create, list, card, delete, validate empty name, navigate | Created date on card |
| Content | Create, expand, edit/save, validate headline, empty state | — |
| AI Draft | Gen button visible, gen succeeds, button hidden, error state | — |
| Review | Approve/Reject/Request visible, approve→APPROVED, reject→REJECTED, req→REVIEWED, edit→DRAFT, buttons hidden for APPROVED | Invalid state transitions → error, Reject/ReqEdits with feedback dialog, `bg-emerald-100`/`bg-red-100`/`bg-yellow-100` assertions |
| Translation | Button visible for APPROVED, language selector options | Translate creates new piece, translated piece has correct language + originalId, translated piece appears in list |
| **WebSocket** | **NONE** | Connection indicator green, state changes broadcast via WebSocket, disconnect/reconnect |
| State Badges | "Does not crash" generic test | All 5 badge colors: DRAFT(gray), SUGGESTED_BY_AI(blue), REVIEWED(yellow), APPROVED(emerald), REJECTED(red), Unknown state fallback (no crash) |
| Edge Cases | Empty name validation, empty headline validation, delete empty campaign | AI draft on non-existent content (error), Review on non-existent content (error) |
| Regression | CSRF, Enum case, Health check | nginx config crash, Docker health check, STATIC_ROOT collectstatic, uv.lock frozen |
| Data Integrity | — | Full workflow persists across restart, Pagination |
| Bug Report | Reporter exists but untested with real failures | Verify reporter output structure |

---

## Implementation Plan

### Part 1: WebSocket Tests (NEW describe block)
**Files:** `frontend/tests/e2e/workflow.spec.ts`

- Test: Connection indicator shows green "Connected" on detail page
- Test: State change broadcasts via WebSocket (toast/notification appears)
- Test: Disconnecting triggers connection state update
- Test: Reconnecting restores connection

Requirement: Tests use `page.route` for WS if possible, or verify WebSocket was created via introspection.

**Risk:** WebSocket mocking in Playwright is complex — Chromium doesn't allow `page.route('ws://...')`. Approach: Use `page.evaluate` to patch `WebSocket` constructor, intercept and inject messages.

### Part 2: State Badge Rendering (expand existing block)
**File:** `frontend/tests/e2e/workflow.spec.ts` (replace generic "does not crash" test)

- Test: DRAFT badge renders with correct display text
- Test: SUGGESTED_BY_AI badge renders as "Suggested"
- Test: REVIEWED badge renders as "Reviewed"
- Test: APPROVED badge renders as "Approved"
- Test: REJECTED badge renders as "Rejected"
- Test: Unknown/fallback state does not crash page

**Risk:** Tests depend on having content in each state. Use `page.evaluate` + GraphQL direct mutations to seed content in required states, or mock responses.

### Part 3: Translation Completeness (expand existing block)
**File:** `frontend/tests/e2e/workflow.spec.ts`

- Test: Selecting language + clicking Translate creates new content piece (verify via list)
- Test: Translated piece shows correct language tag
- Test: Translated piece has `originalId` (verified via expanded card)

**Risk:** The real Translate mutation calls the AI provider. Must intercept via route stub to return a pre-configured response.

### Part 4: State Machine Invalid Transitions
**File:** `frontend/tests/e2e/workflow.spec.ts`

- Test: Approving already-approved content returns error
- Test: Rejecting already-rejected content returns error
- Test: Generating draft on non-DRAFT content (if UI allows) returns error

### Part 5: Non-Existent Content Error Handling
**File:** `frontend/tests/e2e/workflow.spec.ts`

- Test: Generating AI draft for deleted/non-existent content shows error
- Test: Reviewing non-existent content shows error

**Approach:** These need a content ID that doesn't exist. Use `page.evaluate` to directly call GraphQL mutations with a fake ID.

### Part 6: Edge Cases
**File:** `frontend/tests/e2e/workflow.spec.ts`

- Test: Creating content with very long headline (200+ chars) is truncated or rejected
- Test: Creating campaign with very long name (200+ chars) is handled gracefully

### Part 7: Infrastructure Regression (if testable from Playwright)
**File:** `frontend/tests/e2e/workflow.spec.ts`

- Test: Backend serves HTML at port 8000 (not just GraphQL)
- Test: All 3 Docker containers are healthy (requires Docker access — maybe defer to CI)

**Risk:** Docker container checks require shell access which Playwright can't do. Defer to CI or manual verification. Skip if non-trivial.

### Part 8: Bug Report Verification
**File:** `frontend/tests/e2e/bug-reporter.ts` verification

- Create a deliberately failing test run to verify bug-reporter output format
- Verify `agentic/runs/F-028-playwright-e2e/bug-report.md` is created and properly structured

### Part 9: Documentation
**File:** `README.md`

- Add "Playwright E2E Tests" section under Testing
- Add "Bug Reporting" note

---

## Test Execution Order

All tests run headless chromium against `docker compose up` stack:

```bash
# Terminal 1: Start stack
docker compose up --build -d

# Terminal 2: Run E2E
pnpm test:e2e
```

Tests are idempotent (clean DB each run via global-setup). No hardcoded sleeps — all `waitForSelector`/`waitForResponse`.

---

## Dependencies & Risks

| Risk | Impact | Mitigation |
|---|---|---|
| WebSocket mocking hard in Playwright | Tests skipped or brittle | Use `page.evaluate` + patched WS constructor |
| Docker infra not available in CI | E2E tests skipped in CI | Document as manual/local-only |
| State badge colors change | Tests fail on CSS class change | Assert display text not CSS classes |
| AI provider unavailable | Draft/Translate tests fail | Route-stub all AI mutations |
| Bug report reporter has bugs | Report not generated | Test with deliberate failure first |

---

## Task Breakdown

| Step | What | Est. Time |
|---|---|---|
| 1 | Add WebSocket tests (Part 1) | 30min |
| 2 | Add state badge rendering tests (Part 2) | 15min |
| 3 | Complete translation coverage (Part 3) | 15min |
| 4 | Add invalid transition tests (Part 4) | 15min |
| 5 | Add non-existent content error tests (Part 5) | 10min |
| 6 | Verify bug reporter with failure + fix if needed (Part 8) | 10min |
| 7 | Update README (Part 9) | 5min |
| 8 | Run full suite, verify all pass, run again to confirm idempotency | 10min |
| **Total** | | **~1h 50min** |
