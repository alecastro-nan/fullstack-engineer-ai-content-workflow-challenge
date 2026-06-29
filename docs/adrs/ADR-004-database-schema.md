# ADR-004: Database Schema Design

## Status
Accepted

## Context
The platform needs to store campaigns, content pieces, and review state transitions. We need to design the PostgreSQL schema including tables, enums, indices, and relationships. The schema must support the core workflow: Campaign → Content Pieces → AI Draft → Human Review → Approval/Rejection → Translation.

## Decision
We use Django's ORM with the following design:

### Campaigns Table
- UUID primary key (non-sequential, safe for multi-node deployments)
- Soft delete via `isDeleted` boolean flag (preserves referential integrity for translations and reviews)
- Status as VARCHAR (flexible, supports active/archived without migration)
- Indices on `isDeleted` and `status` for filtered queries

### Content Pieces Table
- UUID primary key
- Foreign key to campaigns (PROTECT at DB level — prevents accidental hard deletes; application-level cascade for soft deletes)
- Self-referential foreign key `originalId` for translations (SET_NULL on delete — preserves translation if original is removed)
- State as VARCHAR with Django TextChoices (5 states: draft, suggested_by_ai, reviewed, approved, rejected)
- Soft delete via `isDeleted` boolean with `deletedAt` timestamp
- Indices on `campaignId`, `state`, and `isDeleted` for common query patterns

## Consequences
### Positive
- Soft delete allows undo/recovery and maintains audit trail
- UUIDs avoid sequential ID enumeration attacks
- Self-referential FK cleanly models translations without a separate table
- Django ORM handles migration generation, rollback, and state management
- TextChoices provides type safety and validation at the Django level without requiring PostgreSQL ENUM type changes

### Negative
- UUIDs are larger than integers (128-bit vs 32-bit), impacting index size
- Soft delete requires all queries to filter `isDeleted=False` (error-prone if forgotten)
- Django's CharField with choices doesn't enforce the constraint at the database level (unlike a PostgreSQL ENUM)
- Self-referential FK can create circular references in serialization

## Alternatives Considered
- **Single content table with language variants**: Rejected. Mixing translations into the same row makes it impossible to have independent review states per language. Each translation needs its own review workflow.
- **Separate content pieces per language (linked by originalId)**: Chosen. This is the current design — clean separation, independent state machine per translation, easy to query content in a specific language.
- **State as PostgreSQL ENUM**: Rejected. Django's TextChoices with VARCHAR provides equivalent validation at the application layer without requiring raw SQL migrations for enum changes. PostgreSQL ENUMs require `ALTER TYPE ... ADD VALUE` which is a heavier operation.
- **Integer PKs**: Rejected. UUIDs are preferred for distributed systems and prevent sequential enumeration attacks.

## Schema Overview
### campaigns
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| name | VARCHAR(255) | NOT NULL |
| description | TEXT | |
| status | VARCHAR(50) | active, archived |
| isDeleted | BOOLEAN | soft delete |
| deletedAt | TIMESTAMPTZ | nullable |
| createdAt | TIMESTAMPTZ | |
| updatedAt | TIMESTAMPTZ | |

### content_pieces
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| campaignId | UUID | FK → campaigns.id |
| originalId | UUID | FK → content_pieces.id (for translations) |
| headline | VARCHAR(500) | |
| description | TEXT | |
| body | TEXT | |
| language | VARCHAR(10) | e.g., en, es, fr |
| state | VARCHAR(20) | TextChoices: draft, suggested_by_ai, reviewed, approved, rejected |
| isDeleted | BOOLEAN | soft delete |
| deletedAt | TIMESTAMPTZ | nullable |
| createdAt | TIMESTAMPTZ | |
| updatedAt | TIMESTAMPTZ | |

### Indices
- campaigns: `isDeleted`, `status`
- content_pieces: `campaignId`, `state`, `isDeleted`

## References
- Challenge requirements: "State machine must track: Draft → Suggested by AI → Reviewed → Approved/Rejected"
- Django Model definition: `backend/apps/campaigns/models.py`, `backend/apps/content/models.py`
