# Handoff — F-008: Review state machine + GraphQL review mutations

## Meta
- **From:** Builder
- **To:** Code Reviewer
- **Date:** 2026-06-19 14:00 UTC

## What was done
- `backend/apps/reviews/models.py` — `StateHistory` model (content_piece FK, from_state, to_state, action, feedback, timestamps)
- `backend/apps/reviews/migrations/0001_add_state_history.py` — creates state_history table
- `backend/apps/reviews/services.py` — `ReviewService` with `VALID_TRANSITIONS` map, `review_content(action, feedback)` and `edit_content()` methods
- `backend/apps/reviews/schema.py` — `ReviewMutation` (reviewContent, editContent) and `ReviewQuery` (contentStateHistory)
- `backend/config/schema.py` — wired `ReviewMutation` and `ReviewQuery` into root schema
- `backend/apps/reviews/tests/test_review_service.py` — 26 unit tests for state transitions, validation, history recording
- `backend/apps/reviews/tests/test_review_graphql.py` — 6 GraphQL integration tests for all mutations
- Updated `README.md` with review mutations reference, state transition table
- Updated `docs/architecture-review.md` R-006 status

## Valid transitions enforced
| From | Action | To |
|---|---|---|
| DRAFT | — | (no review actions allowed) |
| SUGGESTED_BY_AI | APPROVE | APPROVED |
| SUGGESTED_BY_AI | REJECT | REJECTED |
| SUGGESTED_BY_AI | REQUEST_EDITS | REVIEWED |
| REVIEWED | APPROVE | APPROVED |
| REVIEWED | REJECT | REJECTED |
| REVIEWED | REQUEST_EDITS | REVIEWED |
| APPROVED | — | (terminal) |
| REJECTED | — | (terminal; edit resets to draft) |

## Documentation updated
- README.md: added review mutations GraphQL examples, state transition table, updated current status
- docs/architecture-review.md: updated R-006 from ⚠️ to ✅

## Not done / known issues
- AI draft generation mutation (F-010) triggers the `draft → suggested_by_ai` transition — not yet implemented
- No WebSocket broadcast on state change (F-017)

## Quality gates
- **98 tests passing** (32 new for reviews, 66 existing)
- **mypy strict**: no errors
- **ruff**: no errors
- **Migration**: `0001_add_state_history` created and applied

## Next actions
1. Code Reviewer: review `backend/apps/reviews/`, verify docs changes
2. Security Reviewer: verify no secrets exposed, input validation adequate
3. Database Reviewer: verify StateHistory schema + indices

## Artifacts
- Migration: `backend/apps/reviews/migrations/0001_add_state_history.py`
- Decision: none needed (follows AGENTS.md Appendix D state machine)
- Feature list: F-008 marked in-progress
