#!/usr/bin/env bash
set -euo pipefail

# ================================================================
# Instalación de skills para ACME Content Workflow Platform
# Basado en: NestJS + React/Vite + Prisma + PostgreSQL + Docker
# ================================================================

echo "=== Instalando skills del stack ==="

# ⚠️  Skills marked CRITICAL by SkillSpector were removed.
# See knowledge/decisions/002-remove-critical-skills.md for details.

# ── NestJS ──
npx skills add jeffallan/claude-skills --skill nestjs-expert -y
npx skills add affaan-m/everything-claude-code --skill nestjs-patterns -y

# ── TypeScript ──
npx skills add wshobson/agents --skill typescript-advanced-types -y
npx skills add github/awesome-copilot --skill javascript-typescript-jest -y

# ── React ──
npx skills add vercel-labs/agent-skills --skill vercel-react-best-practices -y
npx skills add google-labs-code/stitch-skills --skill react:components -y

# ── Vite + Vitest ──
npx skills add antfu/skills --skill vite -y
npx skills add antfu/skills --skill vitest -y

# ── Prisma ──
npx skills add prisma/skills --skill prisma-database-setup -y
npx skills add prisma/skills --skill prisma-client-api -y

# ── PostgreSQL ──
npx skills add wshobson/agents --skill postgresql-table-design -y
npx skills add github/awesome-copilot --skill postgresql-optimization -y

# ── Testing ──
npx skills add github/awesome-copilot --skill playwright-generate-test -y
npx skills add manutej/luxor-claude-marketplace --skill jest-react-testing -y

# ── Docker ──
npx skills add sickn33/antigravity-awesome-skills --skill docker-expert -y
npx skills add github/awesome-copilot --skill multi-stage-dockerfile -y

# ── WebSocket ──
npx skills add jeffallan/claude-skills --skill websocket-engineer -y

# ── Sentry (opcional, para logging/monitoreo) ──
npx skills add getsentry/sentry-for-ai --skill sentry-sdk-setup -y

echo ""
echo "=== Instalación completada ==="
echo "Ejecuta 'npx skills list' para ver las skills instaladas."
