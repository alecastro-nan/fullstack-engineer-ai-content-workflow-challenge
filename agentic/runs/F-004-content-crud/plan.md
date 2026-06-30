# Plan — F-004: Content Piece CRUD GraphQL API

## Status
Pre-implementation plan for Builder.

## Prerequisites
- F-003 complete (Campaign model, services, schema exist ✅)
- `backend/apps/content/` scaffolded with:
  - `models.py` — ContentPiece model exists (needs `default=uuid.uuid4` fix)
  - `admin.py` — ContentPieceAdmin exists ✅
  - `apps.py` — ContentConfig exists ✅
  - App registered in `INSTALLED_APPS` ✅

## Implementation Steps

### Step 1: Fix ContentPiece model
**File: `backend/apps/content/models.py`**
- Add `default=uuid.uuid4` to `id` field (currently missing default)
- Keep all existing fields: campaign FK, headline, description, body, language, state (TextChoices), original FK, created_at, updated_at, is_deleted
- Keep existing Meta: db_table, indexes

### Step 2: Create ContentPiece service layer
**File: `backend/apps/content/services.py`**
- `ContentPieceService` class with static methods
- `_validate_headline(headline)` — strip, check not empty, max 255
- `_validate_language(language)` — strip, check not empty, max 10
- `_validate_campaign(campaign_id)` — check campaign exists and not deleted
- `create_content_piece(campaign_id, headline, description, body, language)` — validates campaign FK and fields, returns ContentPiece with state=DRAFT
- `get_content_piece_by_id(content_id)` — returns single piece (not deleted)
- `list_content_pieces(campaign_id)` — filter by campaign, not deleted, order by -created_at
- `update_content_piece(content_id, headline, description, body, language)` — partial update with validation, returns None if not found
- `soft_delete_content_piece(content_id)` — sets is_deleted=True, update_fields

**Validation rules:**
- headline: required, stripped, max 255 chars
- language: required, stripped, max 10 chars (ISO 639-1 codes)
- campaign_id: must be a valid UUID that references an existing, non-deleted Campaign
- state changes NOT allowed here (handled by F-009/F-010 review mutations)

### Step 3: Create ContentPiece GraphQL schema
**File: `backend/apps/content/schema.py`**

Types:
- `ContentState` — strawberry enum mirroring model State choices
- `ContentPieceInput` — strawberry input (campaignId, headline, description="", body="", language="en")
- `ContentPieceUpdateInput` — strawberry input (headline, description, body, language — all optional)
- `ContentPieceType` — strawberry type with from_model() converter
  - Fields: id (ID), campaignId (ID), headline, description, body, language, state (ContentState), originalId (ID | None), createdAt, updatedAt

Queries:
- `content_pieces(campaignId: ID, page: int=1, perPage: int=20)` → `ContentPiecePage` (paginated, filtered by campaign)
- `contentPiece(id: ID)` → `ContentPieceType | None`

Mutations:
- `create_content_piece(input: ContentPieceInput!)` → `ContentPieceType`
- `update_content_piece(id: ID!, input: ContentPieceUpdateInput!)` → `ContentPieceType | None`
- `delete_content_piece(id: ID!)` → `bool`

Error handling:
- Wrap `ValidationError` as `GraphQLError` in mutations
- Invalid UUID returns None (same pattern as Campaign schema)

### Step 4: Integrate into root schema
**File: `backend/config/schema.py`**
- Import `ContentPieceQueries` and `ContentPieceMutations` from `apps.content.schema`
- Add `ContentPieceQueries` and `ContentPieceMutations` to Query/Mutation class inheritance

### Step 5: Generate migration
```bash
python manage.py makemigrations content
python manage.py migrate content
```

### Step 6: Write tests

**File: `backend/apps/content/tests/test_content_model.py`**
- test_create_content_piece — creates with campaign, verifies all fields, checks state=DRAFT
- test_create_content_piece_strips_whitespace
- test_create_content_piece_rejects_empty_headline
- test_create_content_piece_rejects_headline_too_long
- test_create_content_piece_nonexistent_campaign — raises ValidationError
- test_get_content_piece_by_id
- test_get_content_piece_by_id_returns_none_for_missing
- test_get_content_piece_by_id_returns_none_for_deleted
- test_list_content_pieces — by campaign_id
- test_list_content_pieces_other_campaign — pieces from campaign A not in campaign B
- test_update_content_piece
- test_update_content_piece_rejects_empty_headline
- test_soft_delete_content_piece
- test_soft_delete_nonexistent
- test_content_str

**File: `backend/apps/content/tests/test_content_graphql.py`**
- test_create_content_mutation — creates campaign first, then content
- test_create_content_empty_headline — returns error
- test_create_content_nonexistent_campaign — returns error (campaignId not found)
- test_create_content_invalid_campaign_id — invalid UUID returns None/error
- test_content_pieces_query — list by campaignId
- test_content_piece_query_by_id
- test_content_piece_query_not_found
- test_update_content_mutation
- test_update_content_not_found
- test_update_content_invalid_id
- test_delete_content_mutation — soft deletes, verify query returns None after
- test_delete_content_invalid_id

### Step 7: Quality gates
```bash
ruff check apps/content/
mypy apps/content/
pytest apps/content/tests/ --cov=apps.content --cov-report=term
```

## Known Issues / Decisions
- `id` field missing `default=uuid.uuid4` — model will error on create without fix (Step 1)
- State transitions NOT part of this task — handled in F-009/F-010
- No auth/authorization — out of scope for challenge
- ContentPiece model has `original` FK for translations (used in F-008)

## Estimated Time
~45 minutes (same pattern as F-003, model already scaffolded)
