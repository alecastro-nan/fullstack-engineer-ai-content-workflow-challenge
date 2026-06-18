#!/usr/bin/env bash
set -euo pipefail

# ================================================================
# Instalación de skills para ACME Content Workflow Platform
# Basado en: Django (Python) + Strawberry GraphQL + React/Vite + PostgreSQL + Docker
# ================================================================
# ⚠️  See knowledge/decisions/002-remove-critical-skills.md for security audit history.
# ⚠️  Architecture changed from NestJS/TypeScript to Django/Strawberry GraphQL/Python.
# ⚠️  See knowledge/decisions/003-architecture-replanning.md for details.
# ================================================================

echo "=== Instalando skills del stack ==="

# ── Django + Python ──
npx skills add your-org/django-skills --skill django-best-practices -y 2>/dev/null || echo "WARNING: django-best-practices skill not available yet"
npx skills add your-org/strawberry-skills --skill strawberry-graphql -y 2>/dev/null || echo "WARNING: strawberry-graphql skill not available yet"

# ── TypeScript (frontend) ──
npx skills add wshobson/agents --skill typescript-advanced-types -y
npx skills add github/awesome-copilot --skill javascript-typescript-jest -y

# ── React ──
npx skills add vercel-labs/agent-skills --skill vercel-react-best-practices -y
npx skills add google-labs-code/stitch-skills --skill react:components -y

# ── Vite + Vitest ──
npx skills add antfu/skills --skill vite -y
npx skills add antfu/skills --skill vitest -y

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
