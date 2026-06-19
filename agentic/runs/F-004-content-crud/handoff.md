# Handoff — F-004: Content Piece CRUD GraphQL API

## Meta
- **From:** Builder
- **To:** Code Reviewer, Security Reviewer, Database Reviewer
- **Date:** 2026-06-19

## What was done
- Fixed ContentPiece model: added `default=uuid.uuid4` to `id` field
- Created `ContentPieceService` in `services.py`: create, get, list (by campaign), update, soft_delete with validation (headline, language, campaign FK)
- Created GraphQL schema in `schema.py`: `ContentState` enum, `ContentPieceInput`, `ContentPieceUpdateInput`, `ContentPieceType`, `ContentPiecePage`, queries, mutations
- Integrated `ContentPieceQueries` and `ContentPieceMutations` into root `config/schema.py`
- Migration `0001_initial` created and applied
- 30 tests: 16 model service + 14 GraphQL integration (97% coverage)

## Documentation updated
- README.md: added ContentPiece CRUD API to GraphQL reference, updated Current Status, added Architecture section

## Not done / known issues
- State transitions not implemented (handled in F-009/F-010)
- No auth/authorization (out of scope for challenge)

## Next actions
1. Code Reviewer: review `backend/apps/content/`, verify README changes
2. Security Reviewer: verify no secrets exposed, input validation in place
3. Database Reviewer: verify schema, indices, migration idempotency

## Artifacts
- Migration: `backend/apps/content/migrations/0001_initial.py`
- Service: `backend/apps/content/services.py`
- Schema: `backend/apps/content/schema.py`
- Root schema: `backend/config/schema.py`
- Tests: `backend/apps/content/tests/test_content_model.py`
- Tests: `backend/apps/content/tests/test_content_graphql.py`
