# Decision: 2026-06-19 — Campaign Model: Status Enum, Composite Index, GraphQL Enum

## Context
During F-003 implementation, the Campaign model needed:
- A status field with constrained values (not free text)
- An efficient index for the listing query `filter(is_deleted=False).order_by("-created_at")`
- A matching GraphQL enum type for status

## Decisions
1. **Status as TextChoices**: `Campaign.Status` with `ACTIVE` and `ARCHIVED` values using Django's `TextChoices`, consistent with the `ContentPiece.State` pattern.
2. **Composite index**: `Index(fields=["is_deleted", "-created_at"], name="idx_campaigns_list")` covers the listing query in a single index scan (partitioned by `is_deleted`, ordered by `created_at DESC`).
3. **GraphQL enum**: `CampaignStatus` Strawberry enum mirrors the Django TextChoices, so GraphQL consumers can discover valid values via introspection.
4. **Validation at service layer**: `_validate_status()` checks values against `Campaign.Status.values` before persisting, supporting Django ORM create/update patterns without calling `full_clean()`.

## Rationale
- TextChoices prevents arbitrary strings at the database level (matching ContentPiece pattern).
- Composite index avoids an extra sort operation for the most common read query.
- GraphQL enum provides self-documenting API (frontend discovers valid values).
- Service-layer validation catches errors before the DB round-trip.

## Alternatives Considered
- Plain CharField with no choices: rejected — allows silent data corruption.
- Django `full_clean()`: rejected — doesn't trigger on ORM `.create()`, inconsistent.
- Two separate indexes on `is_deleted` and `created_at`: rejected — composite covers both filter + order in one pass.
