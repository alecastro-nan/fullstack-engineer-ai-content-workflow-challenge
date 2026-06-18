# Plan — F-001: Clean up old NestJS/TypeScript backend artifacts

## Objective
Remove all NestJS/Prisma/TypeScript backend code, configuration, and dependencies to prepare for the Django+Strawberry scaffolding in F-002.

## Steps
1. `git rm` all tracked NestJS files (src/, test/, nest-cli.json, package.json, tsconfig*.json, vitest*.config.ts, drizzle/, pnpm-*)
2. Delete untracked/ignored artifacts (dist/, node_modules/, .env, *.tsbuildinfo)
3. Remove empty src/, test/, drizzle/ directories
4. Update compose.yml: remove commented NestJS backend service, add Django placeholder
5. Update pnpm-workspace.yaml: remove `"backend"` entry
6. Create backend/.gitkeep to preserve directory for F-002
7. Verify: docker compose config, grep for NestJS patterns, clean git status
8. Create handoff.md and audit.log

## Verification
- `docker compose config` succeeds
- `grep -r "nest-cli\|NestFactory\|@nestjs" . --include='*.yml' --include='*.yaml' --include='*.json'` returns nothing
- `git status` shows only intentional changes
- `ls backend/` returns only `.gitkeep`
