# F-000: Initialize Monorepo — Implementation Plan

## Technology Decisions
- **Backend:** NestJS (TypeScript) with Drizzle ORM
- **Frontend:** Vite + React (TypeScript)
- **Real-time:** WebSockets nativos (ws)
- **Package manager:** pnpm
- **Lint/format:** Biome
- **Testing:** Vitest

## Phases & Commits

### Phase A: Pre-work
- Verify symlinks (CLAUDE.md, .cursorrules, copilot-instructions.md → AGENTS.md)
- Verify biome.json and .gitignore
- Create .github/workflows/

### Phase B: Backend scaffold
- Create backend/ directory tree (all modules: campaign, content, ai, review, realtime, common)
- package.json with NestJS + Drizzle + Vitest deps
- tsconfig.json with strict mode
- nest-cli.json, main.ts, app.module.ts
- Stub modules for all features
- drizzle.config.ts, drizzle/.gitkeep, .env.example

### Phase C: Frontend scaffold
- Create frontend/ directory tree
- package.json with Vite + React + Vitest deps
- tsconfig.json with strict mode
- vite.config.ts with proxy config
- index.html, main.tsx, App.tsx
- Types (campaign, content, review), API client, WebSocket stub

### Phase D: Infrastructure
- compose.yml (PostgreSQL service)
- .github/workflows/ci.yml (Biome lint)

### Phase E: Documentation & Handoff
- Update AGENTS.md for Drizzle
- Update nestjs-structure.md, migration-pattern.md, init.sh
- Create decision record
- Create handoff directory and update session-progress.md
