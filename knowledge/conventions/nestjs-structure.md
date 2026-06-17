# Convention: NestJS Module Structure

Every feature module must contain:
- `*.controller.ts` — route handlers
- `*.service.ts` — business logic
- `*.module.ts` — module definition
- `dto/` — Data Transfer Objects with class-validator decorators
- `entities/` — TypeORM entities or Prisma schema references

## Naming Rules
- Controller methods: `create()`, `findAll()`, `findOne()`, `update()`, `remove()`
- Service methods match controller names
- DTOs: `Create{Entity}Dto`, `Update{Entity}Dto`
- Always use validation pipes: `@Body(new ValidationPipe())`

## File Organization
```
campaign/
├── campaign.controller.ts    # Route handlers
├── campaign.service.ts       # Business logic
├── campaign.module.ts        # Module definition
├── dto/
│   ├── create-campaign.dto.ts
│   └── update-campaign.dto.ts
└── entities/
    └── campaign.entity.ts
```
