# ADR-001: REST vs GraphQL

## Status
Superseded by ADR-005

## Context
The ACME Content Workflow platform needs an API style for communication between the frontend and backend. The challenge requires supporting CRUD operations, AI draft generation, review actions, and real-time updates. The non-negotiable rule R-001 mandates Django + Strawberry GraphQL for the backend.

## Decision
Use Strawberry GraphQL (native GraphQL for Django) as the sole API layer.

### Rationale
- Strawberry GraphQL is the native GraphQL implementation for Django, providing type-safe schema generation from Python types
- GraphQL allows flexible queries for content workflows (e.g., fetch campaign with only specific fields)
- Reduces over-fetching compared to REST endpoints
- Single endpoint simplifies frontend API client configuration
- Strawberry's Django integration auto-generates resolvers from Django models

## Consequences
### Positive
- Flexible queries reduce frontend-backend churn
- Type-safe schema via Python type annotations
- Built-in GraphQL playground for development
- Single endpoint simplifies deployment and monitoring

### Negative
- GraphQL query complexity can impact performance (mitigation: query depth limiting, pagination)
- Caching is more complex than REST (use DataLoader for N+1 prevention)
- Learning curve for team unfamiliar with GraphQL

## Alternatives Considered
- **REST only**: Rejected — would require multiple endpoints per resource; Strawberry GraphQL is the required approach per ADR-005
- **Both REST + GraphQL**: Rejected — unnecessary complexity for a single-client architecture

## References
- ADR-005: Django + Strawberry GraphQL Architecture
- AGENTS.md R-001: Backend must be Django with Strawberry GraphQL
