#!/usr/bin/env bash
set -euo pipefail

# ================================================================
# Skill installation for ACME Content Workflow Platform
# Based on: Django (Python) + Strawberry GraphQL + React/Vite + PostgreSQL + Docker
# ================================================================
# ⚠️  See knowledge/decisions/002-remove-critical-skills.md for security audit history.
# ⚠️  Architecture changed from NestJS/TypeScript to Django/Strawberry GraphQL/Python.
# ⚠️  See docs/adrs/ADR-005-django-strawberry-architecture.md for architecture details.
# ================================================================

echo "=== Installing stack skills ==="

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

# ── Sentry (optional, for logging/monitoring) ──
npx skills add getsentry/sentry-for-ai --skill sentry-sdk-setup -y

echo ""
echo "=== Installation complete ==="
echo "Run 'npx skills list' to see installed skills."
