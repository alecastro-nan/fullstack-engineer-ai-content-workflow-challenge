# Plan — F-029: Frontend Quality Polish

## Overview
Address four frontend-only quality issues identified in code review: React Error Boundary, empty catch block, reconnection cap, and unused variable.

**Estimated time:** 25-30min
**Stack:** frontend
**Role:** builder → @typescript-reviewer → @code-reviewer → doc update

## Part 1 — ErrorBoundary Component

### Current state
`App.tsx` renders `<Routes>` directly with no error boundary. Any unhandled React error causes a white screen. See `frontend/src/App.tsx:6-12`.

### Action
Create `frontend/src/components/ErrorBoundary.tsx`:

```tsx
import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <h1>Something went wrong</h1>
          <p>An unexpected error occurred.</p>
          <button onClick={() => window.location.reload()}>Reload page</button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

### Where to wrap
In `App.tsx` — wrap the `<Routes>` block:

```tsx
import { ErrorBoundary } from './components/ErrorBoundary';

export function App() {
  return (
    <ErrorBoundary>
      <Routes>
        ...
      </Routes>
    </ErrorBoundary>
  );
}
```

### Test plan
- Unit test at `src/components/ErrorBoundary.test.tsx`:
  - Renders children normally when no error
  - Renders fallback UI when child throws
  - "Reload page" button calls `window.location.reload` (mock via `vi.fn()`)

## Part 2 — Fix Empty Catch Block

### Current state
`frontend/src/services/websocket.ts:100-101`:
```typescript
catch {
  // ignore malformed messages
}
```
Violates R-012 (no silent empty catch blocks).

### Action
Replace with:
```typescript
catch {
  console.warn('Malformed WebSocket message:', e);
}
```

## Part 3 — Cap Reconnection Attempts

### Current state
`frontend/src/services/websocket.ts:155` — `state.reconnectAttempts += 1` never capped. Can reconnect indefinitely.

### Action
Add cap check at the start of `scheduleReconnect`:
```typescript
private scheduleReconnect(contentId: string): void {
    const state = this.connections.get(contentId);
    if (!state) return;

    if (state.reconnectTimer) return;

    const MAX_RECONNECT_ATTEMPTS = 20;
    if (state.reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      this.setStatus(contentId, 'disconnected');
      this.connections.delete(contentId);
      return;
    }
    // ... rest of existing logic
}
```

### Test plan
- Reconnect stops after 20 attempts without errors
- Malformed message handler calls `console.warn`

## Part 4 — Remove Unused Variable

### Current state
`frontend/src/hooks/useWebSocket.ts:42`:
```typescript
const stableStatus = status;
```
Returned as `{ status: stableStatus, lastEvent }` at line 44. The intermediate variable is unnecessary.

### Action
Remove line 42, change return to:
```typescript
return { status, lastEvent };
```

## Acceptance Criteria Summary

| # | Criterion | Verification |
|---|---|---|
| 1 | ErrorBoundary at `src/components/ErrorBoundary.tsx` | File exists |
| 2 | Wraps entire app in `App.tsx` | Code inspection |
| 3 | Fallback UI: "Something went wrong" + "Reload page" | Test + visual |
| 4 | Empty catch → `console.warn('Malformed WebSocket message:', e)` | Test + code |
| 5 | Reconnect capped at 20 attempts | Test + code |
| 6 | `stableStatus` removed | Code inspection |
| 7 | `pnpm typecheck` — 0 errors | CLI |
| 8 | All 88 frontend tests pass | CLI |

## Quality Gates
- `pnpm typecheck` — 0 errors
- `pnpm test` — all 88+ passing (88 existing + new ErrorBoundary tests)
- `pnpm build` — success
- `pnpm lint` — 0 errors
- No backend changes

## Files to modify
| File | Change |
|---|---|
| `frontend/src/components/ErrorBoundary.tsx` | **NEW** — ErrorBoundary component |
| `frontend/src/components/ErrorBoundary.test.tsx` | **NEW** — unit tests |
| `frontend/src/App.tsx` | Wrap `<Routes>` in `<ErrorBoundary>` |
| `frontend/src/services/websocket.ts` | Fix catch block + add reconnect cap |
| `frontend/src/hooks/useWebSocket.ts` | Remove `stableStatus` |

## Risks
- ErrorBoundary uses class component pattern (required for `getDerivedStateFromError`) — consistent with React docs
- `window.location.reload` mock in test needs `vi.spyOn(window.location, 'reload')`
- No backend, infra, or DB changes
