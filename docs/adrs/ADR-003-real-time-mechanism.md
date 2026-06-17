# ADR-003: Real-Time Mechanism

## Status
Proposed

## Context
The platform must show updates to all users in real-time when content state changes (AI draft generated, review action taken, translation completed). We need to choose a mechanism for real-time communication.

## Decision
[To be filled during implementation — choose one: WebSockets / SSE / GraphQL Subscriptions]

## Consequences
### Positive
- [to be filled]

### Negative
- [to be filled]

## Alternatives Considered
- WebSockets (Socket.io): [pros/cons]
- Server-Sent Events (SSE): [pros/cons]
- GraphQL Subscriptions: [pros/cons]
- Polling (long-polling): [pros/cons]

## References
- Challenge requirements section "Real-time features with WebSockets, GraphQL Subscriptions, or SSE"
- Skill: `harness/skills/real-time.md`
