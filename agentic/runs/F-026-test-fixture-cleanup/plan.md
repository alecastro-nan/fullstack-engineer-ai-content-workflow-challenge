# Plan — F-026: Test & Fixture Cleanup

## Overview

Clean up test dummy API key prefixes (`sk-test-*` → `test-invalid-*`) to avoid false-positive secret scanner alerts, and close coverage gaps identified by code review in `reviews/schema.py` and `anthropic_provider.py`.

**Estimated time:** 30-40min
**Stack:** test

## Part 1 — Dummy Key Rename (`sk-` → `test-invalid-`)

### Problem
14 occurrences of `sk-` prefixed dummy keys across 6 files. These trigger false-positive alerts in secret scanners (gitLeaks, truffleHog, etc.) because `sk-` matches real OpenAI/Anthropic key patterns. Renaming to `test-invalid-` eliminates the false positives.

### Files to modify

| File | Lines | Current Pattern | Target |
|---|---|---|---|
| `.github/workflows/ci.yml` | 79-80 | `sk-test-fake-key`, `sk-ant-test-fake-key` | `test-invalid-fake-key`, `test-invalid-ant-fake-key` |
| `apps/reviews/tests/test_review_graphql.py` | 65, 95, 125 | `sk-test-key` | `test-invalid-key` |
| `apps/ai/tests/test_ai_service.py` | 26, 45, 63, 64, 99, 115, 137, 138, 162 | `sk-test-key` (×7), `sk-ant-test-key` (×2) | `test-invalid-key`, `test-invalid-ant-key` |
| `apps/ai/tests/test_ai_draft_mutation.py` | 57 | `sk-test-key` | `test-invalid-key` |
| `apps/ai/tests/test_ai_translate_mutation.py` | 60 | `sk-test-invalid-key-do-not-use` | `test-invalid-key-do-not-use` |
| `tests/test_e2e_workflow.py` | 59 | `sk-test-e2e-key` | `test-invalid-e2e-key` |

### Action
Replace each `sk-test-` prefix with `test-invalid-`, `sk-ant-test-` with `test-invalid-ant-`. Add comment `# Test-only dummy key — not a real credential` to each assignment.

## Part 2 — Coverage Gaps: `reviews/schema.py`

**Current coverage:** 77% (14 of 62 lines missed)

### Uncovered lines and test strategy

| Lines | Code | Test Approach |
|---|---|---|
| 36-37 | `except ValueError: raise GraphQLError("Invalid content piece ID")` in `content_state_history` | Call `contentStateHistory` with a non-UUID string (`"not-a-uuid"`) — assert error message |
| 40 | `return []` when piece is None or not owner | Call `contentStateHistory` with a valid UUID that does not exist in the DB — assert empty list |
| 70-71 | `except ValueError` in `review_content` | Call `reviewContent` with a non-UUID string — assert error message |
| 81-82 | `except ValidationError as e` in `review_content` | Mock `ReviewService.review_content` to raise `ValidationError` — assert GraphQLError bubbles up (existing test framework supports mocking) |
| 84 | `return None` after successful ReviewService call returns None | Mock `ReviewService.review_content` to return `None` — assert mutation returns `None` |
| 99-100 | `except ValueError` in `edit_content` | Call `editContent` with a non-UUID string — assert error message |
| 103 | `return None` for unauthorized in `edit_content` | Call `editContent` with a campaign not owned by the auth'd user — assert `None` |
| 111-112 | `except ValidationError as e` in `edit_content` | Mock `ReviewService.edit_content` to raise `ValidationError` — assert GraphQLError bubbles up |
| 114 | `return None` after edit_content returns None | Mock `ReviewService.edit_content` to return `None` — assert mutation returns `None` |

### Estimated tests to add: 7-8 new test cases
- 2 bad UUID tests (reuse pattern, can test both query and mutations in one test)
- 1 not-found / unauthorized list test
- 2 ValidationError propagation tests (review + edit)
- 2 None-return tests (review + edit)
- (Optional) unauthorized owner test for edit_content

## Part 3 — Coverage Gaps: `anthropic_provider.py`

**Current coverage:** 58% (24 of 57 lines missed)

### Uncovered lines and test strategy

| Lines | Code | Test Approach |
|---|---|---|
| 30-40 | `translate()` text parsing — `headline`/`description` extraction | Call `translate()` with various `text` formats (missing Headline:, missing Description:, both present) — verify correct parsing |
| 50-56 | `_call_api` rate limit detection (`"rate"` or `"429"` in error) | Mock `self.client.messages.create` to raise an exception with `"rate limit"` in the message — assert `RateLimitError` raised |
| 64 | `if not content: raise MalformedResponseError("...empty response")` | Mock `self.client.messages.create` to return a response with empty content blocks — assert `MalformedResponseError` |
| 71-72 | `_parse_draft_response` JSONDecodeError | Call `_parse_draft_response` with non-JSON string — assert `MalformedResponseError` |
| 82-88 | `_parse_translation_response` JSONDecodeError | Call `_parse_translation_response` with non-JSON string — assert `MalformedResponseError` |

### Estimated tests to add: 6-7 new test cases
- 2 translate parsing tests (headline only, description only, both)
- 1 rate limit error test
- 1 empty response error test
- 2 JSON parse error tests (draft + translate)
- (Optional) generic API error propagation (non-rate-limit exception)

## Quality Gates

- `ruff check backend/` — 0 errors
- `mypy backend/` — 0 errors
- `pytest --cov=apps/reviews/schema.py` — ≥80% coverage
- `pytest --cov=apps/ai/providers/anthropic_provider.py` — ≥75% coverage
- `pnpm test` — 88/88 frontend tests still pass
- `pnpm typecheck` — 0 errors
- Manual grep for `sk-` in test files — only false-positive-safe patterns remain (or none)
- All dummy key assignments have the comment `# Test-only dummy key — not a real credential`

## Risks / Dependencies

- None — no schema, model, or behavioral changes. All work is test-only.
- The `sk-ant-test-*` keys in CI must match exactly what the Anthropic SDK checks for. The rename to `test-invalid-ant-*` is safe because these are dummy keys never actually sent to the API (mocked in unit tests, not reached in E2E).
