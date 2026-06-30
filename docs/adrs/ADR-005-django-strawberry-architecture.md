# ADR-005: Django + Strawberry GraphQL Architecture

## Status
Accepted

## Context
The ACME Content Workflow platform originally planned a NestJS (TypeScript) backend with REST endpoints. However, the challenge requirements mandate:
- Backend must be Django (Python) with Strawberry GraphQL (non-negotiable rule R-001)
- PostgreSQL as the database
- Support for AI-powered drafting and translation

The existing project had NestJS scaffolding with Drizzle ORM, Vitest for testing, and REST API design patterns. This ADR documents the migration from NestJS/TypeScript to Django/Python/Strawberry GraphQL.

## Decision
Adopt Django (Python) + Strawberry GraphQL as the backend stack, replacing NestJS (TypeScript) completely.

### Key Technology Choices
| Concern | Decision | Rationale |
|---|---|---|
| Backend framework | Django 5.x | Mature Python web framework with built-in ORM, admin, migrations |
| API layer | Strawberry GraphQL | Native GraphQL for Django; type-safe with Python generics |
| Database ORM | Django ORM | Built-in, no external ORM needed; migrations included |
| Real-time | Django Channels | Native WebSocket support for Django |
| Testing | pytest + pytest-django | Industry standard for Django testing |
| Type checking | mypy (strict mode) | PEP 484 static type checking |
| Code quality | ruff | Fast Python linter (replaces Biome for backend) |
| Package manager | uv | Fast Python dependency resolver (replaces pnpm for backend) |

### Folder Structure Change
```
Old (NestJS):                      New (Django):
backend/src/campaign/              backend/apps/campaigns/
  campaign.controller.ts              models.py
  campaign.service.ts                 schema.py (GraphQL)
  campaign.module.ts                  mutations.py
  dto/*.ts                            queries.py
  entities/*.ts                       admin.py
```

## Consequences

### Positive
- Challenge requirement R-001 satisfied (Django + Strawberry GraphQL)
- Django ORM provides built-in migrations, admin interface, and PostgreSQL support
- Strawberry GraphQL provides type-safe GraphQL schema generation from Python types
- Django Channels provides native WebSocket support without additional infrastructure
- Python ecosystem has mature AI/ML libraries (openai, anthropic SDKs)
- Built-in Django admin provides quick data inspection without building UIs
- `uv` provides fast, reliable Python dependency management

### Negative
- Existing NestJS scaffolding and tests must be discarded
- Team must be proficient in Python/Django rather than TypeScript/NestJS
- Django ORM is less performant than raw SQL for complex queries (mitigation: use `.select_related()` and `.prefetch_related()`)
- Django Channels requires Redis for production channel layers

### Tradeoffs
- **GraphQL over REST**: GraphQL was chosen over REST because Strawberry is natively supported in Django, and the challenge requires justification of API style. GraphQL provides flexible queries for content workflows and reduces over-fetching.
- **Django ORM over raw SQL**: Django ORM was chosen for developer productivity, built-in migrations, and admin interface. Raw SQL can be used for performance-critical queries via `connection.execute()`.
- **pytest over Django's built-in TestCase**: pytest was chosen for fixture support, parameterized tests, and broader ecosystem.

## Alternatives Considered
- **NestJS (TypeScript)**: Rejected per challenge requirement R-001
- **FastAPI (Python)**: Rejected per challenge requirement R-001 (must be Django + Strawberry GraphQL)
- **Fiber (Go)**: Rejected per challenge requirement R-001
- **REST + Swagger**: Rejected in favor of Strawberry GraphQL as required by architecture

## References
- AGENTS.md R-001: Backend must be Django (Python) with Strawberry GraphQL
- AGENTS.md section 5: Updated folder structure for Django apps
- knowledge/conventions/django-structure.md: Django app structure conventions
- feature_list.json F-025: Architecture replanning task
