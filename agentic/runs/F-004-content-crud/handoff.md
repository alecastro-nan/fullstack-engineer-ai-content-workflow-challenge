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

## Post-review fixes applied
- `on_delete=CASCADE` → `PROTECT` (data safety)
- Composite indexes: `idx_content_campaign_list`, `idx_content_deleted_created`, `idx_content_campaign_state`
- `deleted_at` field added to ContentPiece model
- `original` FK: `db_index=True`
- `select_related("campaign")` in service methods (N+1 prevention)
- `from_model` uses raw FK column values (`campaign_id`, `original_id`)
- Body/description length validation (5KB desc, 50KB body)
- `update_fields` tracking in `update_content_piece` (race condition fix)
- Pagination raises `GraphQLError` instead of silent clamping
- UUID error handling: all mutations raise `GraphQLError` for invalid UUIDs
- Migration `0002` applied (indexes, field changes)
- 36 tests (6 new), 97% coverage
- Language validation tests, blank headline update test, body/desc length tests

## Not done / known issues
- State transitions not implemented (handled in F-009/F-010)
- No auth/authorization (out of scope for challenge)

## Next actions
1. Code Reviewer: review `backend/apps/content/`, verify README changes, confirm fixes applied
2. Security Reviewer: verify M-1 (CASCADE→PROTECT), M-2 (body/desc limits), L-1 (update_fields)
3. Database Reviewer: verify composite indexes, migration 0002

## Artifacts
- Migration: `backend/apps/content/migrations/0001_initial.py`
- Service: `backend/apps/content/services.py`
- Schema: `backend/apps/content/schema.py`
- Root schema: `backend/config/schema.py`
- Tests: `backend/apps/content/tests/test_content_model.py`
- Tests: `backend/apps/content/tests/test_content_graphql.py`
