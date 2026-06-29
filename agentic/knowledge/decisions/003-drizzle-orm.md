# Decision: 2025-06-17 - Use Drizzle ORM (DEPRECATED)

## Status
Superseded by ADR-005 — Django + Strawberry GraphQL Architecture

The project migrated from NestJS/TypeScript (Drizzle ORM) to Django/Python (Django ORM).
This decision is retained for historical reference only.

## Context
The project needs a TypeScript ORM for PostgreSQL. AGENTS.md originally specified Prisma,
but the human decided to use Drizzle ORM instead.

## Decision
Use Drizzle ORM for database access and migrations.

## Rationale
- Drizzle is lighter weight than Prisma (no code generation server)
- SQL-like syntax with full type safety
- Better suited for serverless and edge environments
- Supports raw SQL when needed
- Migration files are plain SQL for full control

## Files affected
- `backend/drizzle/` (schema and migrations)
- `backend/drizzle.config.ts` (Drizzle Kit config)
- `init.sh` (migration command)
