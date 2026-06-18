# Decision: 2025-06-17 - Use Drizzle ORM

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
