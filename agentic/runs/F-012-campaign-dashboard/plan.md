# F-012 + F-013 Frontend Implementation Plan

## Overview
Build the two core frontend pages on the existing Vite/React/TypeScript scaffold, consuming the already-built Django/Strawberry GraphQL backend.

## Branch
`feat/F-012-campaign-dashboard` (from `feat/agentic-plan`)

## F-012: Campaign Dashboard (list + create) — ~2.5h

| Step | What | Est. |
|---|---|---|
| 1 | Create `graphqlRequest<T>` helper in `src/services/api.ts` | 15m |
| 2 | Create query/mutation constants in `src/services/queries.ts` (snake_case aliased to camelCase) | 10m |
| 3 | Create `StatusBadge` reusable component | 10m |
| 4 | Create `CampaignCard` component (clickable card, status badge, date) | 20m |
| 5 | Create `CreateCampaignModal` (form, validation, mutation) | 25m |
| 6 | Create `CampaignDashboard` page (loading/error/empty/data states) | 25m |
| 7 | Wire routes in `App.tsx` | 10m |
| 8 | Tests + typecheck + lint | 25m |

## F-013: Campaign Detail (content pieces, state badges) — ~2.5h

| Step | What | Est. |
|---|---|---|
| 1 | Add detail/mutation queries to `queries.ts` | 10m |
| 2 | Create `ContentStateBadge` component (color-coded) | 15m |
| 3 | Create `ContentCard` component (expand/collapse, edit, save) | 25m |
| 4 | Create `CreateContentModal` (headline+description form) | 20m |
| 5 | Create `CampaignDetail` page (campaign header + content list) | 30m |
| 6 | Wire inline editing + mutations | 15m |
| 7 | Tests + typecheck + lint | 25m |

## Key Risks
1. **snake_case ↔ camelCase**: GraphQL returns snake_case, TS types use camelCase. Mitigation: field aliasing in queries.
2. **Tailwind CSS**: Check if configured — if not, add 15m setup step.
3. **Mutation input fields**: `ContentPieceInput` needs `campaign_id` as key, not `campaignId`.
4. **Campaign detail needs 2 queries**: campaign(id) + contentPieces(campaignId) — fetch in parallel.

## Relevant Files
- `frontend/src/services/api.ts` — existing axios client
- `frontend/src/types/` — Campaign, ContentPiece, ContentState types (camelCase)
- `frontend/src/App.tsx` — current minimal route table
- `frontend/src/pages/` — empty (add CampaignDashboard.tsx, CampaignDetail.tsx)
- `frontend/src/components/` — stub directories exist
