# Skill: Database Migration Patterns

## Purpose
Learn how to create and run database migrations using Prisma, TypeORM, or Alembic.

## When to Use
- When creating the initial schema (F-003)
- When modifying the database schema
- When adding new tables, columns, indices, or enums

## Steps

### 1. Using Prisma (NestJS/TypeScript)
```bash
# Define schema in prisma/schema.prisma
# Create migration
npx prisma migrate dev --name add-campaigns-table

# Apply in production
npx prisma migrate deploy

# Rollback (Prisma does not support rollback natively — use
# `prisma migrate diff` to generate a down migration manually)
```

### 2. Using TypeORM (NestJS/TypeScript)
```bash
# Generate migration from entities
npx typeorm migration:generate src/migrations/CreateCampaigns

# Run migrations
npx typeorm migration:run

# Revert last migration
npx typeorm migration:revert
```

### 3. Using Alembic (FastAPI/Python)
```bash
# Auto-generate migration
alembic revision --autogenerate -m "create_campaigns_table"

# Apply
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

### 4. Migration Best Practices
- Test migrations on a clean database before applying to production
- Each migration should be reversible (up AND down)
- Never edit existing migrations — create a new one
- Use transactions for migrations that modify multiple tables
- Enums: use PostgreSQL ENUM type (not strings in app code)

## Verification
- `pnpm db:migrate` runs without errors
- `pnpm db:rollback` reverts changes
- Schema matches the entity definitions
- Data is preserved across migrations (when expected)
