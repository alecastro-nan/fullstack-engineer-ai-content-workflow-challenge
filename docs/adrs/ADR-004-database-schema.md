# ADR-004: Database Schema Design

## Status
Proposed

## Context
The platform needs to store campaigns, content pieces, and review state transitions. We need to design the PostgreSQL schema including tables, enums, indices, and relationships.

## Decision
[To be filled during implementation]

## Consequences
### Positive
- [to be filled]

### Negative
- [to be filled]

## Alternatives Considered
- Single content table with language variants: [pros/cons]
- Separate content pieces per language (linked by originalId): [pros/cons]
- State as string vs PostgreSQL ENUM: [pros/cons]

## Schema Overview
### campaigns
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| name | VARCHAR(255) | NOT NULL |
| description | TEXT | |
| status | VARCHAR(50) | active, archived |
| isDeleted | BOOLEAN | soft delete |
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
| state | content_state | ENUM |
| isDeleted | BOOLEAN | soft delete |
| createdAt | TIMESTAMPTZ | |
| updatedAt | TIMESTAMPTZ | |

### content_state ENUM
`draft`, `suggested_by_ai`, `reviewed`, `approved`, `rejected`

## References
- Challenge requirements section "State machine must track: Draft → Suggested by AI → Reviewed → Approved/Rejected"
- Skill: `harness/skills/state-machine.md`
- Skill: `harness/skills/migration-pattern.md`
