# Handoff — F-026: Test & Fixture Cleanup

## Meta
- **From:** Builder
- **To:** Code Reviewer
- **Date:** 2025-06-26 10:45 UTC

## What was done

### Part 1 — Dummy Key Rename
- 14 occurrences of `sk-*` prefixed dummy API keys renamed to `test-invalid-*` across 6 files
- Files: `.github/workflows/ci.yml`, `apps/reviews/tests/test_review_graphql.py`, `apps/ai/tests/test_ai_service.py`, `apps/ai/tests/test_ai_draft_mutation.py`, `apps/ai/tests/test_ai_translate_mutation.py`, `tests/test_e2e_workflow.py`
- Each assignment annotated with `# Test-only dummy key — not a real credential`
- Verified: `rg -n "sk-test|sk-ant"` returns no matches

### Part 2 — reviews/schema.py coverage (77% → 97%)
7 new tests in `apps/reviews/tests/test_review_graphql.py`:
- `test_content_state_history_bad_uuid` — bad UUID returns error (lines 36-37)
- `test_content_state_history_not_found` — non-existent UUID returns `[]` (line 40)
- `test_review_content_bad_uuid` — bad UUID returns error (lines 70-71)
- `test_review_content_invalid_transition` — approve DRAFT without AI generation triggers ValidationError (lines 81-82)
- `test_edit_content_bad_uuid` — bad UUID returns error (lines 99-100)
- `test_edit_content_not_owned` — different user returns None (line 103)
- `test_edit_content_no_fields_triggers_validation` — no fields triggers ValidationError (lines 111-112)

### Part 3 — anthropic_provider.py coverage (58% → 100%)
10 new tests in `apps/ai/tests/test_anthropic_provider.py`:
- Draft: success, malformed JSON, empty response, rate limit, generic API error
- Translate: success, parsing both present, missing headline, missing description, malformed JSON

## Documentation updated
- `agentic/knowledge/learnings/2026-06-26-sk-prefix-false-positive.md` — learning entry

## Not done / known issues
- Lines 84 and 114 in reviews/schema.py remain uncovered (97% not 100%) — these are defensive `if result is None: return None` checks after a TOCTOU race condition that occurs if a piece is deleted between the schema's existence check and the service call. Virtually impossible to reproduce in tests.

## Next actions
1. Code Reviewer: verify test quality + assertion meaningfulness + no `sk-` patterns remain
2. Security Reviewer: confirm no real key patterns in test files

## Quality gates (all passing)
| Gate | Result |
|---|---|
| ruff | 0 errors |
| mypy (82 files) | 0 errors |
| pytest (backend) | 161/161 |
| pnpm typecheck | 0 errors |
| pnpm test (frontend) | 88/88 |
| reviews/schema.py coverage | 97% (≥80% target) |
| anthropic_provider.py coverage | 100% (≥75% target) |

## Artifacts
- Plan: `agentic/runs/F-026-test-fixture-cleanup/plan.md`
- Learning: `agentic/knowledge/learnings/2026-06-26-sk-prefix-false-positive.md`
- New test file: `backend/apps/ai/tests/test_anthropic_provider.py`
