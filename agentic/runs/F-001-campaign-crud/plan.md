# Plan — F-001: Campaign CRUD API

## Objective
Implement full CRUD REST API for campaigns with NestJS + Drizzle ORM + PostgreSQL.

## Phases
### Phase 1 — Database Schema & Migration
- Drizzle schema for `campaigns` table (id, name, description, status, createdAt, updatedAt, isDeleted)
- DB migration (sql file + Drizzle config pointing to entity files)

### Phase 2 — Database Module
- Global `DatabaseModule` with `DatabaseService` wrapping pg Pool + Drizzle client
- Connection management with `onModuleInit` lifecycle hook

### Phase 3 — DTOs & Validation
- `CreateCampaignDto` (name required, description optional)
- `UpdateCampaignDto` (all optional, partial)
- class-validator decorators for validation

### Phase 4 — Service Layer
- `CampaignService` with CRUD methods
- Paginated `findAll` with `page`/`limit` params
- NotFoundException for missing entities
- Soft-delete in `remove`

### Phase 5 — Controller & Wiring
- `CampaignController` with standard REST routes
- `@HttpCode(204)` for DELETE
- `ParseUUIDPipe` for id params
- `CampaignModule` exports controller + service
- `AppModule` imports DatabaseModule + CampaignModule

### Phase 6 — Testing
- Unit tests: mock drizzle client, test all service methods
- E2E tests: supertest against real DB, test all endpoint + error cases
- Add SWC to vitest configs for `emitDecoratorMetadata` support

## Key Decisions
- Soft-delete with `isDeleted` flag, filtered out in all queries
- `@Global()` DatabaseModule so features can inject without re-importing
- SWC transformer in vitest (esbuild doesn't emit `design:paramtypes`)
- Direct service instantiation in unit tests (no NestJS DI overhead)
