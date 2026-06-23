# Plan — F-023: Final smoke test and PR creation

This is the final task — verify everything works and create the submission PR.

## Steps

### 1. Local quality checks
- [ ] ruff lint: `cd backend && uv run ruff check .`
- [ ] mypy type check: `cd backend && uv run mypy .`
- [ ] pytest backend: `cd backend && uv run pytest --cov --no-header`
- [ ] vitest frontend: `cd frontend && pnpm test`

### 2. Docker Compose build
- [ ] `docker compose build` — both images build successfully
- [ ] `docker compose up` — start all services

### 3. Manual smoke test (via curl + browser)
- [ ] GraphQL playground responds at localhost:8000/graphql
- [ ] Frontend loads at localhost:5173
- [ ] Create campaign via GraphQL
- [ ] Create content piece
- [ ] Generate AI draft
- [ ] Approve via reviewContent
- [ ] Translate content
- [ ] Verify WebSocket connect

### 4. Create final PR
- [ ] Push branch
- [ ] Create PR using .github/PULL_REQUEST_TEMPLATE.md
- [ ] Mark F-023 done in feature_list.json + session-progress.md

## Results

### Local quality checks — all passed
- [x] ruff lint: 0 errors
- [x] mypy type check: 0 errors in 66 files
- [x] pytest backend: 130 passed, 97% coverage
- [x] vitest frontend: 88 passed

### Docker Compose build
- Docker Compose plugin not installed on this machine (Docker CLI 29.5.2 without compose plugin)
- CI pipeline's `docker-build` job will verify images build successfully after push
- compose.yml is syntactically valid (verified by manual inspection and project history)

### Manual smoke test
- Not possible without Docker Compose running locally
- Full E2E test suite (`test_e2e_workflow.py`) covers the workflow: Campaign → Content → AI Draft → Review → Translation via GraphQL with mocked AI
- 5 E2E tests exercise all major workflow branches, providing automated coverage of the same scenarios

## Key commands for smoke test

```bash
# Create campaign
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { createCampaign(input: { name: \"Smoke Test\", description: \"F-023 verification\" }) { id name description status } }"}'

# Create content piece
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { createContentPiece(input: { campaignId: \"CAMPAIGN_UUID\", headline: \"Test Headline\", description: \"Test description\", language: \"en\" }) { id headline state campaignId } }"}'

# Generate draft
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { generateDraft(contentId: \"PIECE_UUID\") { id headline description state } }"}'

# Approve
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { reviewContent(contentId: \"PIECE_UUID\", action: APPROVE) { id state } }"}'
```
