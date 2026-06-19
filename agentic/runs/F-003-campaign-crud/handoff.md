# Handoff — F-003: Campaign CRUD GraphQL API

## Meta
- **From:** Builder
- **To:** Code Reviewer
- **Date:** 2026-06-19 12:40 UTC

## What was done
- Campaign model with UUID PK, Status TextChoices (ACTIVE/ARCHIVED), composite index `(is_deleted, -created_at)`, explicit index names
- CampaignService: create_campaign, get_campaign_by_id, list_campaigns, update_campaign, soft_delete_campaign — with empty-name validation, name length validation (max 255), status validation against enum
- GraphQL schema: CampaignStatus (GraphQL enum), CampaignType, CampaignInput, CampaignUpdateInput, CampaignPage
- Query `campaigns(page, perPage)` — paginated list with bounds validation (1-100)
- Query `campaign(id)` — single campaign
- Mutation `createCampaign(input)` — creates campaign, wraps ValidationError as GraphQLError
- Mutation `updateCampaign(id, input)` — updates campaign, wraps ValidationError as GraphQLError
- Mutation `deleteCampaign(id)` — soft deletes campaign with update_fields optimization
- Integration into root schema via class inheritance
- Migration 0001_initial created and applied
- 28 tests: 16 model service tests + 10 GraphQL integration tests
- Coverage: 98% on apps.campaigns

## Post-review fixes applied (based on @code-reviewer, @security-reviewer, @database-reviewer)
- Campaign.Status TextChoices enum for status field
- Composite index `idx_campaigns_list` on (is_deleted, -created_at) for listing query
- GraphQL CampaignStatus enum (strawberry @enum)
- Status validation in update_campaign service method
- Name max length validation (255 chars)
- `save(update_fields=[...])` on soft delete
- Pagination bounds: page >= 1, per_page 1-100
- ValidationError wrapped as GraphQLError in schema mutations
- `raise ... from e` pattern for exception chaining (ruff B904)
- New tests: invalid UUID, campaign not found, invalid status, name too long, __str__

## Not done / known issues
- No authentication/authorization (out of scope for F-003, pending ADR or later phase)
- GraphiQL introspection enabled in dev (production will disable via settings)
- No rate limiting (out of scope for challenge)

## Quality gates
- ruff: All checks passed ✅
- mypy: Success: no issues found ✅
- pytest: 30 passed (including 2 existing health tests) ✅
- Coverage: 98% ✅

## Next actions
1. Mark F-003 as done in feature_list.json and session-progress.md (done)
2. Proceed to F-004: Content Piece CRUD GraphQL API

## Files changed
- `backend/apps/campaigns/models.py` — Status TextChoices, composite index, explicit names
- `backend/apps/campaigns/services.py` — NEW: service layer with validations
- `backend/apps/campaigns/schema.py` — CampaignStatus enum, CampaignPage, error wrapping
- `backend/config/schema.py` — integrated campaign queries/mutations
- `backend/apps/campaigns/tests/test_campaign_model.py` — 16 tests
- `backend/apps/campaigns/tests/test_campaign_graphql.py` — 10 tests
- `backend/pyproject.toml` — ruff exclude for migrations
- `backend/apps/campaigns/migrations/0001_initial.py` — NEW: migration
