# Plan — F-032: Minor Code Quality Polish

## Meta
- **Task ID:** F-032
- **Branch:** `feat/F-032-code-quality-polish`
- **Dependencies:** None
- **Est. time:** ~30min
- **Reviewers:** @code-reviewer, @typescript-reviewer (for frontend items)

## Overview

Address 5 small code quality issues from the PR #1 audit. Each change touches a single file and has no dependencies on the others.

---

## Work Items (in recommended order)

### 1. Fix state_change payload shape (M-6)
**File:** `backend/apps/ws/consumers.py`

**Current:**
```python
async def state_change(self, event: dict[str, object]) -> None:
    payload = event.get("payload", {})
    msg: dict[str, object] = {"type": "state.change"}
    msg.update(payload)  # type: ignore[call-overload]
    await self.send_json(msg)
```

**Target:**
```python
async def state_change(self, event: dict[str, object]) -> None:
    payload = event.get("payload", {})
    await self.send_json({
        "type": "state.change",
        "contentId": payload.get("contentId", ""),
        "campaignId": payload.get("campaignId", ""),
        "oldState": payload.get("oldState", ""),
        "newState": payload.get("newState", ""),
        "action": payload.get("action", ""),
        "timestamp": payload.get("timestamp", ""),
    })
```

**Why:** Removes the `# type: ignore[call-overload]` suppression, prevents payload key leaks, makes the message shape explicit and self-documenting.

---

### 2. Fix TranslatePanel visibility (M-7)
**Files:** `frontend/src/components/ContentList/ContentPieceCard.tsx` (line containing `{isApproved && onTranslate &&`)
- Change condition from `isApproved` to `(contentState === 'SUGGESTED_BY_AI' || contentState === 'APPROVED')`
- Backend mutation already allows translation from any state, so this is a frontend-only change

**Note:** The state check should match the backend's `ContentState` enum values (UPPER_CASE in frontend types).

---

### 3. Add feedback parameter to editContent (M-9)
**Files:**
- `backend/apps/reviews/schema.py` — add `feedback: str | None = None` parameter to `editContent` mutation
- `backend/apps/reviews/services.py` — pass `feedback` through to `StateHistory.objects.create()`

**Current signature:**
```python
def edit_content(self, info, content_id, headline=None, description=None, body=None) -> ContentPieceType | None:
```

**Target:**
```python
def edit_content(self, info, content_id, headline=None, description=None, body=None, feedback=None) -> ContentPieceType | None:
```

The `ReviewAction.EDIT` history record should include the feedback text.

---

### 4. Unify pagination validation (M-10)
**Files:**
- `backend/apps/campaigns/schema.py` — currently coerces invalid values
- `backend/apps/content/schema.py` — currently raises `GraphQLError`

**Decision:** Use coercion (like campaigns) — it's more user-friendly for a GraphQL API. Update `content/schema.py` to coerce instead of raising:
```python
if page < 1:
    page = 1
if per_page < 1 or per_page > MAX_PER_PAGE:
    per_page = 20
```

**Alternative:** Use error pattern in both. If changing, update both files to match.

---

### 5. Remove duplicate ContentState type (M-12)
**File:** `frontend/src/types/review.ts` — remove the `ContentState` type definition

**Also check:** `frontend/src/components/ReviewActions/ReviewActions.tsx` and any other file importing from `review.ts` — ensure they import from `content.ts` instead:
- `review.ts` exports: `ContentState` → remove it (only type in file)
- If `review.ts` becomes empty after removal, it can be kept as an empty file or removed if nothing imports from it

**Note:** After removing, run `tsc --noEmit` to verify no imports break.

---

## Files Changed (complete list)

| File | Change |
|---|---|
| `backend/apps/ws/consumers.py` | Explicit payload shape in state_change |
| `frontend/src/components/ContentList/ContentPieceCard.tsx` | Translation button visibility condition |
| `backend/apps/reviews/schema.py` | Add `feedback` parameter to editContent |
| `backend/apps/reviews/services.py` | Pass feedback to StateHistory |
| `backend/apps/campaigns/schema.py` | (Maybe) unify pagination validation |
| `backend/apps/content/schema.py` | (Maybe) unify pagination validation |
| `frontend/src/types/review.ts` | Remove duplicate ContentState |

---

## Testing Strategy

All tests are existing test suites — verify no regressions, and add/update as needed for new behavior.

| Item | Test verification |
|---|---|
| 1 | WS test asserts exact keys returned (no extra keys) |
| 2 | Component test renders TranslatePanel for SUGGESTED_BY_AI and APPROVED |
| 3 | Service test verifies StateHistory.feedback is set on edit |
| 4 | Pagination test expects coercion, not error, after change |
| 5 | `tsc --noEmit` passes after removing type |

## Risk Assessment

Low risk — all changes are small and well-understood. The editContent feedback parameter is the only behavioral change (previously feedback was silently ignored). No migration needed since feedback is optional.
