# Plan — F-003: Campaign CRUD GraphQL API

## Steps
1. Fix model: add `default=uuid.uuid4` to UUIDField
2. Create service layer (`services.py`) with CRUD methods + validation
3. Complete GraphQL schema: inputs (`CampaignInput`, `CampaignUpdateInput`), queries (`campaigns`, `campaign`), mutations (`createCampaign`, `updateCampaign`, `deleteCampaign`)
4. Integrate into root schema (`config/schema.py`) via class inheritance
5. Generate + run migration
6. Write tests: model unit tests + GraphQL query/mutation tests
7. Run quality gates: ruff, mypy, pytest
8. Create handoff directory

## Dependencies
- F-002 (Django + Strawberry stack) — DONE

## Deliverables
- `apps/campaigns/models.py` — Campaign model with UUID PK
- `apps/campaigns/services.py` — CampaignService class
- `apps/campaigns/schema.py` — Strawberry types, queries, mutations
- `config/schema.py` — Root schema with campaign integration
- `apps/campaigns/migrations/0001_initial.py` — Migration
- `apps/campaigns/tests/test_campaign_model.py` — 14 model tests
- `apps/campaigns/tests/test_campaign_graphql.py` — 7 GraphQL tests
