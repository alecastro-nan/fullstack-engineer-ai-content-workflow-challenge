# Skill: State Machine Implementation

## Purpose
Learn how to implement the content review state machine with valid transition guards and state enforcement.

## When to Use
- When implementing the review state machine (F-007)
- When adding review endpoints (F-008)
- When adding new states or transitions

## Steps

### 1. Define State Enum
- Use database enum type (PostgreSQL ENUM or Prisma enum)
- States: `draft`, `suggested_by_ai`, `reviewed`, `approved`, `rejected`
- Map enum values in the application layer

### 2. Valid Transitions
```
draft → suggested_by_ai        (AI draft generated)
suggested_by_ai → reviewed     (human reviewed)
suggested_by_ai → rejected     (human rejected)
reviewed → approved            (approved after review)
reviewed → rejected            (rejected after review)
reviewed → suggested_by_ai     (re-request AI changes)
rejected → draft               (edit and resubmit)
rejected → suggested_by_ai     (try different AI approach)
approved → (no further transitions)
```

### 3. Guards Implementation
- Create a `StateMachine` service/class
- Method `canTransition(from: State, to: State): boolean`
- Method `transition(contentId, to: State)` that validates + updates
- Throw `InvalidTransitionError` with message for invalid moves
- Use a transition map (object/dictionary) for O(1) lookup

### 4. State History (Optional)
- Create `content_state_history` table
- Columns: id, contentId, fromState, toState, changedBy, comment, createdAt
- Log every transition for audit trail

### 5. Error Handling
- `InvalidTransitionError` → HTTP 422 Unprocessable Entity
- Include current state and allowed next states in error response
- Never silently swallow invalid transitions

## Verification
- All valid transitions work end-to-end
- All invalid transitions return 422
- State persists correctly after each transition
- Unit tests cover every transition in the map
