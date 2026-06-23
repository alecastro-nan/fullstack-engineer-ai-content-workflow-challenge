# Plan — F-013: Campaign Detail Page (Content Pieces, State Badges)

## Summary

Implement the Campaign Detail page at `/campaigns/:id` showing a single campaign's metadata (name, description, status) plus a list of all associated content pieces with their review states (draft, suggested_by_ai, reviewed, approved, rejected). Users can create new content pieces via a modal form, view/edit content fields inline, and see color-coded state badges on each piece. This task is purely frontend — it consumes the existing backend GraphQL queries/mutations without modifying backend schema.

---

## 1. Files to Create

### 1.1 New Types — `frontend/src/types/content.ts`

| Field | Purpose |
|---|---|
| `ContentState` | Union type: `'draft' \| 'suggested_by_ai' \| 'reviewed' \| 'approved' \| 'rejected'` |
| `ContentPiece` | Interface matching `ContentPieceType` from backend schema |
| `ContentPiecePage` | Interface for paginated response |

### 1.2 New GraphQL Queries — `frontend/src/services/queries.ts` (append)

Add these query strings:

- **`CAMPAIGN_QUERY`** — Fetches single campaign by ID (uses existing `campaign(id)` query)
- **`CONTENT_PIECES_QUERY`** — Fetches paginated content pieces by campaign ID (uses existing `contentPieces(campaignId)` query)
- **`CREATE_CONTENT_PIECE_MUTATION`** — Uses existing `createContentPiece` mutation
- **`UPDATE_CONTENT_PIECE_MUTATION`** — Uses existing `updateContentPiece` mutation

### 1.3 New Page — `frontend/src/pages/CampaignDetail.tsx`

The main page component rendered at `/campaigns/:id`.

**Responsibilities:**
- Extract `id` from URL params via `useParams()`
- Fetch campaign metadata via `CAMPAIGN_QUERY`
- Fetch content pieces via `CONTENT_PIECES_QUERY`
- Manage loading, error, and empty states
- Orchestrate content piece creation, selection, editing
- Render header section (campaign info)
- Render content list section

**No new hooks file needed** — the data-fetching logic lives inline in `CampaignDetail.tsx` (following the same pattern as `CampaignDashboard.tsx`). If complexity grows, extract into `useCampaign(id)` and `useContentPieces(campaignId)` hooks in a future task.

### 1.4 New Components

| Component | File | Props | Responsibilities |
|---|---|---|---|
| `ContentStateBadge` | `frontend/src/components/ContentList/ContentStateBadge.tsx` | `{ state: ContentState }` | Renders a pill badge with color-coded background/text based on ContentState |
| `ContentPieceCard` | `frontend/src/components/ContentList/ContentPieceCard.tsx` | `{ content: ContentPiece, onSelect: (id: string) => void, onUpdate: (id: string, headline: string, description: string) => Promise<void>, isSelected: boolean }` | Displays headline, language, state badge, creation date. Click expands to show inline edit form |
| `CreateContentModal` | `frontend/src/components/ContentList/CreateContentModal.tsx` | `{ open: boolean, onClose: () => void, onCreate: (headline: string, description: string) => Promise<void> }` | Modal form with headline (required), description (optional). Follows same pattern as `CreateCampaignModal` |
| `ContentList` | `frontend/src/components/ContentList/ContentList.tsx` | `{ pieces: ContentPiece[], selectedId: string \| null, onSelect: (id: string) => void, onUpdate: (id: string, headline: string, description: string) => Promise<void>, loading: boolean }` | Renders the list of ContentPieceCards. Handles empty state and loading skeleton |
| Barrel export | `frontend/src/components/ContentList/index.ts` | — | Re-exports `ContentStateBadge`, `ContentPieceCard`, `ContentList`, `CreateContentModal` |

### 1.5 Component Directory Structure

```
frontend/src/components/ContentList/
├── index.ts
├── ContentStateBadge.tsx
├── ContentStateBadge.test.tsx
├── ContentPieceCard.tsx
├── ContentPieceCard.test.tsx
├── ContentList.tsx
├── ContentList.test.tsx
├── CreateContentModal.tsx
├── CreateContentModal.test.tsx
```

---

## 2. Files to Modify

| File | Change |
|---|---|
| `frontend/src/App.tsx` | Add route: `<Route path="/campaigns/:id" element={<CampaignDetail />} />` |
| `frontend/src/services/queries.ts` | Append 4 new GraphQL query strings (see section 4) |
| `frontend/src/types/campaign.ts` | No changes needed (Campaign type is sufficient) |
| `frontend/src/pages/CampaignDashboard.tsx` | No changes needed (already navigates to `/campaigns/:id` via CampaignCard) |
| `frontend/README.md` | Add Campaign Detail page description + document state badge colors (see documentation_requirements) |

---

## 3. Components — Detailed Specs

### 3.1 ContentStateBadge

```typescript
// frontend/src/components/ContentList/ContentStateBadge.tsx

import type { ContentState } from '../../types/content';

const STATE_STYLES: Record<ContentState, { bg: string; text: string; label: string }> = {
  draft:           { bg: 'bg-gray-100',    text: 'text-gray-700',  label: 'Draft' },
  suggested_by_ai: { bg: 'bg-blue-100',    text: 'text-blue-800',  label: 'Suggested' },
  reviewed:        { bg: 'bg-yellow-100',  text: 'text-yellow-800', label: 'Reviewed' },
  approved:        { bg: 'bg-emerald-100', text: 'text-emerald-800',label: 'Approved' },
  rejected:        { bg: 'bg-red-100',     text: 'text-red-800',   label: 'Rejected' },
};

interface ContentStateBadgeProps {
  state: ContentState;
}

export function ContentStateBadge({ state }: ContentStateBadgeProps) {
  const styles = STATE_STYLES[state];
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${styles.bg} ${styles.text}`}>
      {styles.label}
    </span>
  );
}
```

**Color mapping per acceptance criteria:**

| State | BG Color | Text Color | Display Label |
|---|---|---|---|
| `draft` | gray-100 | gray-700 | Draft |
| `suggested_by_ai` | blue-100 | blue-800 | Suggested |
| `reviewed` | yellow-100 | yellow-800 | Reviewed |
| `approved` | emerald-100 | emerald-800 | Approved |
| `rejected` | red-100 | red-800 | Rejected |

### 3.2 ContentPieceCard

```typescript
// frontend/src/components/ContentList/ContentPieceCard.tsx

import type { ContentPiece } from '../../types/content';
import { ContentStateBadge } from './ContentStateBadge';

interface ContentPieceCardProps {
  content: ContentPiece;
  isSelected: boolean;
  onSelect: (id: string) => void;
  onUpdate: (id: string, headline: string, description: string) => Promise<void>;
}
```

**States to render:**
- **Collapsed (default):** Shows headline, language tag, ContentStateBadge, creation date, expand caret
- **Expanded (when `isSelected`):** Shows all collapsed info + inline editable fields for headline and description + Save/Cancel buttons
- **Saving:** Disable Save button, show "Saving..." text
- **Error:** Show error message below the form if `onUpdate` rejects

### 3.3 ContentList

```typescript
// frontend/src/components/ContentList/ContentList.tsx

import type { ContentPiece } from '../../types/content';
import { ContentPieceCard } from './ContentPieceCard';

interface ContentListProps {
  pieces: ContentPiece[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onUpdate: (id: string, headline: string, description: string) => Promise<void>;
  loading: boolean;
}
```

**States to render:**
- **Loading:** 3 skeleton rows (same as CampaignDashboard pattern — `animate-pulse` boxes)
- **Empty:** "No content pieces yet — add your first piece" with a call-to-action button that opens the CreateContentModal
- **Populated:** Stack of ContentPieceCards with spacing

### 3.4 CreateContentModal

```typescript
// frontend/src/components/ContentList/CreateContentModal.tsx

interface CreateContentModalProps {
  open: boolean;
  onClose: () => void;
  onCreate: (headline: string, description: string) => Promise<void>;
}
```

**Behavior:** Identical pattern to `CreateCampaignModal.tsx` — modal overlay with form fields (headline required, description optional), validation, submit button, cancel, error display, and cleanup on close.

### 3.5 CampaignDetail (page)

```typescript
// frontend/src/pages/CampaignDetail.tsx
```

**Internal state:**
- `campaign: Campaign | null`
- `contentPieces: ContentPiece[]`
- `selectedPieceId: string | null`
- `loading: boolean`
- `error: string | null`
- `createModalOpen: boolean`

**Data fetching:**
- On mount, extract `id` from `useParams()`
- Fetch campaign + content pieces in a **single batched GraphQL request**:
  ```graphql
  query CampaignDetail($id: ID!, $campaignId: ID!) {
    campaign(id: $id) { id name description status createdAt updatedAt }
    contentPieces(campaignId: $campaignId, page: 1, perPage: 50) {
      items { id campaignId headline description body language state originalId createdAt updatedAt }
      totalCount
    }
  }
  ```
  This is a valid single GraphQL request that fetches both datasets at once.

**States to render:**
- **Loading:** Full-page skeleton (header skeleton + 3 content piece skeletons)
- **Error:** Error banner with "Back to campaigns" link
- **Campaign not found (404):** "Campaign not found" message with "Back to campaigns" link
- **Loaded:** Campaign header + ContentList + Create button

---

## 4. GraphQL Queries/Mutations — Full Definitions

```graphql
# CAMPAIGN_QUERY — Single campaign by ID
query CampaignDetail($id: ID!) {
  campaign(id: $id) {
    id
    name
    description
    status
    createdAt
    updatedAt
  }
}

# CONTENT_PIECES_QUERY — All content pieces for a campaign (non-deleted, newest first)
query ContentPieces($campaignId: ID!, $page: Int!, $perPage: Int!) {
  contentPieces(campaignId: $campaignId, page: $page, perPage: $perPage) {
    items {
      id
      campaignId
      headline
      description
      body
      language
      state
      originalId
      createdAt
      updatedAt
    }
    totalCount
    page
    perPage
  }
}

# CREATE_CONTENT_PIECE_MUTATION
mutation CreateContentPiece($input: ContentPieceInput!) {
  createContentPiece(input: $input) {
    id
    campaignId
    headline
    description
    body
    language
    state
    originalId
    createdAt
    updatedAt
  }
}

# UPDATE_CONTENT_PIECE_MUTATION
mutation UpdateContentPiece($id: ID!, $input: ContentPieceUpdateInput!) {
  updateContentPiece(id: $id, input: $input) {
    id
    campaignId
    headline
    description
    body
    language
    state
    originalId
    createdAt
    updatedAt
  }
}
```

**Note on field naming:** The backend `ContentPieceType` uses `created_at` (snake_case) but the frontend `Campaign` type uses `createdAt` (camelCase). Check whether the backend schema returns snake_case or if a camelCase middleware is in place. Looking at `CampaignType.from_model()`, it uses `created_at` (snake_case) in the response. The existing frontend `CAMPAIGNS_QUERY` queries `createdAt` — verify in GraphQL playground whether the schema aliases these.

**⚠️ Risk:** If backend fields are `created_at` but frontend queries use `createdAt`, this will fail silently. The plan assumes the GraphQL schema exposes `createdAt` (camelCase) as seen in the existing working queries. If not, the query strings must use `created_at` (matching `CampaignType.from_model()` field names).

**Validation:** Before implementing, run:
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __type(name: \"ContentPieceType\") { fields { name } } }"}'
```
to confirm the exact field names exposed by the schema.

---

## 5. State Management

### Design Decision: Local state only (no React Context)

- **Rationale:** Campaign Detail is a single page with no sibling or ancestor components that need shared state. All state is local to `CampaignDetail.tsx`.
- **State shape in `CampaignDetail.tsx`:**
  - `campaign` — fetched campaign object (`useState<Campaign | null>`)
  - `pieces` — fetched content pieces (`useState<ContentPiece[]>`)
  - `selectedPieceId` — currently expanded card (`useState<string | null>`)
  - `loading` / `error` — fetch status
  - `createModalOpen` — modal visibility
- **Data flow:** After creating a content piece, prepend it to `pieces` state (optimistic local update). After editing, replace in-place in the `pieces` array.
- **No URL query state** — the selected piece is local state only, not reflected in the URL (TBD for future F-014/F-015 where this might change).

### Future Concern (out of scope for F-013)

Tasks F-014 (AI Draft), F-015 (Review UI), and F-016 (Translation) will all need to read/write content piece state. If state management gets complex, **migrate to React Context** or a thin state machine (useReducer) at that point. For now, keep it simple with local useState and prop drilling.

---

## 6. Test Plan

### Test File Locations

| Test File | Component | Est. Tests |
|---|---|---|
| `frontend/src/components/ContentList/ContentStateBadge.test.tsx` | ContentStateBadge | 6 |
| `frontend/src/components/ContentList/ContentPieceCard.test.tsx` | ContentPieceCard | 6 |
| `frontend/src/components/ContentList/ContentList.test.tsx` | ContentList | 4 |
| `frontend/src/components/ContentList/CreateContentModal.test.tsx` | CreateContentModal | 6 |
| `frontend/src/pages/CampaignDetail.test.tsx` | CampaignDetail page | 4 |

**Total: ~26 test cases**

### ContentStateBadge (6 tests)

1. Renders "Draft" with gray styling for `draft` state
2. Renders "Suggested" with blue styling for `suggested_by_ai` state
3. Renders "Reviewed" with yellow styling for `reviewed` state
4. Renders "Approved" with green styling for `approved` state
5. Renders "Rejected" with red styling for `rejected` state
6. Renders fallback styling for unknown state (type cast)

### ContentPieceCard (6 tests)

1. Renders headline and language tag
2. Renders state badge with correct state
3. Calls `onSelect` when card is clicked
4. Renders inline edit form when `isSelected` is true
5. Save button calls `onUpdate` with modified values
6. Cancel button hides inline edit form

### ContentList (4 tests)

1. Renders list of ContentPieceCards
2. Shows empty state when pieces array is empty
3. Shows loading skeleton when `loading` is true
4. Passes `onSelect` and `onUpdate` to each card

### CreateContentModal (6 tests)

1. Does not render when `open` is false
2. Renders form fields when `open` is true (headline + description)
3. Shows validation error when headline is empty and submit clicked
4. Calls `onCreate` with headline and description
5. Calls `onClose` when cancel is clicked
6. Displays error message when `onCreate` fails

### CampaignDetail Page (4 tests — integration-level)

1. Renders campaign header with name and description
2. Renders content piece list fetched from campaign
3. Shows error state when fetch fails
4. Creates a content piece and refreshes the list

### Testing Patterns to Follow

- Use `@testing-library/react` with `render`, `screen`
- Use `userEvent.setup()` for user interactions (matching `CreateCampaignModal.test.tsx` pattern)
- Use `MemoryRouter` for components that use `useNavigate`/`useParams`
- Mock `graphqlRequest` at the module level with `vi.mock('../../services/api')`
- For `CampaignDetail.test.tsx`, provide mock campaign and content piece data
- Match the test patterns established in `frontend/src/components/CampaignList/*.test.tsx`

---

## 7. Order of Implementation

### Step 1: Define types — `frontend/src/types/content.ts`
**Size:** XS (<15 min)
**Action:** Create ContentState union type and ContentPiece interface.
**Acceptance:** `pnpm typecheck` passes with new types.

### Step 2: Add GraphQL queries — `frontend/src/services/queries.ts`
**Size:** XS (<15 min)
**Action:** Append CAMPAIGN_QUERY, CONTENT_PIECES_QUERY, CREATE_CONTENT_PIECE_MUTATION, UPDATE_CONTENT_PIECE_MUTATION.
**Acceptance:** Query strings are syntactically valid GraphQL.

### Step 3: Build ContentStateBadge component + tests
**Size:** S (<30 min)
**Action:** Create component file, test file, and barrel export.
**Acceptance:** All 6 badge tests pass. Visual check: each state has correct color.

### Step 4: Build ContentPieceCard component + tests
**Size:** M (~45 min)
**Action:** Create card with collapsed/expanded states, inline edit form.
**Acceptance:** All 6 card tests pass. Manual check: click card expands, edit saves.

### Step 5: Build ContentList component + tests
**Size:** S (<30 min)
**Action:** Create list wrapper with loading/empty/populated states.
**Acceptance:** All 4 list tests pass.

### Step 6: Build CreateContentModal component + tests
**Size:** S (<30 min)
**Action:** Modal form matching CreateCampaignModal pattern.
**Acceptance:** All 6 modal tests pass.

### Step 7: Build CampaignDetail page + tests
**Size:** M (~45 min)
**Action:** Wire up route, data fetching, compose components.
**Acceptance:** Page renders with campaign info + content list; create piece works end-to-end.

### Step 8: Wire route in App.tsx
**Size:** XS (<5 min)
**Action:** Add `<Route path="/campaigns/:id" element={<CampaignDetail />} />`.
**Acceptance:** Clicking a CampaignCard navigates to `/campaigns/:id` and renders the detail page.

### Step 9: Documentation update — README.md
**Size:** XS (<10 min)
**Action:** Add Campaign Detail page description + state badge color reference table.
**Acceptance:** README documents the new page and badge meanings.

### Step 10: Run quality gates
**Size:** XS (<10 min)
**Action:** `pnpm typecheck` + `pnpm test` + `pnpm build`
**Acceptance:** All pass with 0 errors.

---

## 8. Risks and Edge Cases

### 8.1 Backend Field Naming Mismatch

**Risk:** The backend `ContentPieceType.from_model()` returns snake_case fields (`created_at`, `updated_at`, `campaign_id`, `original_id`), but the frontend query might expect camelCase (`createdAt`, `updatedAt`, `campaignId`, `originalId`).

**Mitigation:** 
- Check existing `CAMPAIGNS_QUERY` — it queries `createdAt`, `updatedAt` and it works, meaning the GraphQL schema uses camelCase aliases.
- Verify with an introspection query before implementing.
- If fields are snake_case, adjust query strings accordingly.

**Decision to make:** The existing `campaign(id)` query returns `CampaignType` which has fields `created_at`, `updated_at` (snake_case in the Python source). Yet the frontend `CAMPAIGNS_QUERY` uses `createdAt`. Either Strawberry auto-camelCases, or the resolver defines aliases. We'll match whatever the existing `CAMPAIGNS_QUERY` pattern uses.

### 8.2 Content Pieces Without Campaign (Orphaned Data)

**Risk:** If `campaign(id)` returns null (deleted or invalid ID), the page must handle gracefully.

**Mitigation:** Check `campaign` is non-null before rendering. Show "Campaign not found" with a back link if null.

### 8.3 Empty Content Pieces List

**Risk:** New campaign with no content pieces renders an empty list.

**Mitigation:** ContentList handles empty state with "No content pieces yet" + create button.

### 8.4 Large Number of Content Pieces

**Risk:** 50+ content pieces could cause slow rendering.

**Mitigation:** Fetch with `perPage: 50` (practical max for a detail view). Pagination is not required for MVP but the query supports it. Note in code: // TODO: add pagination if needed for campaigns with 50+ pieces

### 8.5 Stale Data After Create/Edit

**Risk:** After creating or editing a piece, the local state must stay in sync with the server.

**Mitigation:** 
- On create: `setPieces((prev) => [newPiece, ...prev])` — optimistic local prepend.
- On edit: `setPieces((prev) => prev.map((p) => (p.id === updated.id ? updated : p)))` — in-place replacement.
- If the request fails, show error but keep the previous state (the card still shows old data; no destructive rollback needed for MVP).

### 8.6 Concurrent Updates (Future)

**Risk:** F-018 (real-time WebSocket) will overlap with this component tree.

**Mitigation:** The selected piece state (`selectedPieceId`) and pieces array will be consumed by the WebSocket update handler in F-018. Design `CampaignDetail.tsx` so the pieces state can be updated externally (via a callback or context) when real-time events arrive. For now, expose a `updatePieceInList` helper function that can be passed down or lifted into a context in F-018.

### 8.7 Navigation Without Data

**Risk:** User navigates directly to `/campaigns/:id` (not from dashboard).

**Mitigation:** The page fetches campaign by ID on mount — it does not rely on prior navigation. This is the primary data path anyway.

---

## Appendix A — ContentPiece Type Definition

```typescript
// frontend/src/types/content.ts

export type ContentState = 
  | 'draft'
  | 'suggested_by_ai'
  | 'reviewed'
  | 'approved'
  | 'rejected';

export interface ContentPiece {
  id: string;
  campaignId: string;
  headline: string;
  description: string;
  body: string;
  language: string;
  state: ContentState;
  originalId: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface ContentPiecePage {
  items: ContentPiece[];
  totalCount: number;
  page: number;
  perPage: number;
}
```

---

## Appendix B — GraphQL Query Strings to Add to `queries.ts`

```typescript
export const CAMPAIGN_QUERY = `
  query Campaign($id: ID!) {
    campaign(id: $id) {
      id
      name
      description
      status
      createdAt
      updatedAt
    }
  }
`;

export const CONTENT_PIECES_QUERY = `
  query ContentPieces($campaignId: ID!, $page: Int!, $perPage: Int!) {
    contentPieces(campaignId: $campaignId, page: $page, perPage: $perPage) {
      items {
        id
        campaignId
        headline
        description
        body
        language
        state
        originalId
        createdAt
        updatedAt
      }
      totalCount
      page
      perPage
    }
  }
`;

export const CREATE_CONTENT_PIECE_MUTATION = `
  mutation CreateContentPiece($input: ContentPieceInput!) {
    createContentPiece(input: $input) {
      id
      campaignId
      headline
      description
      body
      language
      state
      originalId
      createdAt
      updatedAt
    }
  }
`;

export const UPDATE_CONTENT_PIECE_MUTATION = `
  mutation UpdateContentPiece($id: ID!, $input: ContentPieceUpdateInput!) {
    updateContentPiece(id: $id, input: $input) {
      id
      campaignId
      headline
      description
      body
      language
      state
      originalId
      createdAt
      updatedAt
    }
  }
`;
```

---

## Appendix C — Route Wiring in `App.tsx`

```typescript
// frontend/src/App.tsx
import { Navigate, Route, Routes } from 'react-router-dom';
import { CampaignDashboard } from './pages/CampaignDashboard';
import { CampaignDetail } from './pages/CampaignDetail';

export function App() {
  return (
    <Routes>
      <Route path="/" element={<CampaignDashboard />} />
      <Route path="/campaigns/:id" element={<CampaignDetail />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
```

---

## Appendix D — Directory Structure After Implementation

```
frontend/src/
├── components/
│   ├── CampaignList/          # existing
│   └── ContentList/           # NEW
│       ├── index.ts           # barrel export
│       ├── ContentStateBadge.tsx
│       ├── ContentStateBadge.test.tsx
│       ├── ContentPieceCard.tsx
│       ├── ContentPieceCard.test.tsx
│       ├── ContentList.tsx
│       ├── ContentList.test.tsx
│       ├── CreateContentModal.tsx
│       └── CreateContentModal.test.tsx
├── pages/
│   ├── CampaignDashboard.tsx  # existing
│   └── CampaignDetail.tsx     # NEW
├── services/
│   ├── api.ts                 # existing (no change)
│   └── queries.ts             # MODIFIED (append 4 queries)
└── types/
    ├── campaign.ts            # existing
    └── content.ts             # NEW
```

---

## Total Estimated Time: ~3.5 hours

| Step | Time | Dependencies |
|---|---|---|
| 1. Types | 15min | None |
| 2. Queries | 15min | Step 1 |
| 3. ContentStateBadge | 30min | Step 1 |
| 4. ContentPieceCard | 45min | Step 1, 3 |
| 5. ContentList | 30min | Step 4 |
| 6. CreateContentModal | 30min | Step 1 |
| 7. CampaignDetail page | 45min | Steps 2, 5, 6 |
| 8. Route wiring | 5min | Step 7 |
| 9. README update | 10min | Step 7 |
| 10. Quality gates | 10min | All |
| **Total** | **~3h 35min** | |
