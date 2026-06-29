# Plan — F-033: PR Review Issue Remediation

> Address all 17 issues from PR #1 code review + security review.
> All changes are config/docs fixes — no runtime logic.
> Branch from `feat/agentic-plan`, merge back to it.

## Order of Operations

Issues are ordered by dependency (simpler ones first to unblock verification).

---

### Step 1: Symlink fix — `.github/copilot-instructions.md`

**Context:** The symlink target `../../agentic/AGENTS.md` resolves 2 dirs up from `.github/` (outside the repo). Should be `../agentic/AGENTS.md`.

**Change:**
```bash
ln -sf ../agentic/AGENTS.md .github/copilot-instructions.md
```
Also need to verify: `ls -la .github/copilot-instructions.md` shows correct path.

---

### Step 2: Symlink command in AGENTS.md Appendix A

**Context:** The documented command at AGENTS.md line ~955 has the same wrong path. Future agents recreating symlinks will break Copilot.

**Change:** In `agentic/AGENTS.md`, replace:
```
ln -sf ../../agentic/AGENTS.md .github/copilot-instructions.md
```
with:
```
ln -sf ../agentic/AGENTS.md .github/copilot-instructions.md
```

---

### Step 3: Deprecate stale Drizzle ORM decision

**Context:** `agentic/knowledge/decisions/003-drizzle-orm.md` documents using Drizzle (TypeScript/Node.js), but the project uses Django ORM (Python). Anyone reading without full context is misled.

**Change:** Add `## Status` header at top of the file:
```markdown
## Status
Superseded by ADR-005 — Django + Strawberry GraphQL Architecture

The project migrated from NestJS/TypeScript (Drizzle ORM) to Django/Python (Django ORM).
This decision is retained for historical reference only.
```

---

### Step 4: Create `docs/architecture.md`

**Context:** AGENTS.md §5 lists `docs/architecture.md` with "High-level architecture diagram (Mermaid)" but the file doesn't exist. `docs/architecture-review.md` exists with a different purpose.

**Change:** Create `docs/architecture.md` with a Mermaid diagram showing:
- PostgreSQL → Django + Strawberry GraphQL backend → React/Vite frontend
- WebSocket (Django Channels) for real-time
- AI Provider abstraction (OpenAI + Anthropic)
- Basic request flow: GraphQL mutation → resolver → service → DB

---

### Step 5: Handoff template artifact path fix

**Context:** AGENTS.md §7.2.3 handoff template shows `backend/drizzle/0000_init/` — references old stack.

**Change:** Replace with:
```
- Migration: `backend/apps/campaigns/migrations/0001_initial.py`
```

---

### Step 6: Spanish → English in install scripts

**Context:** `install-skills.sh` and `agentic/install-skills.sh` contain Spanish comments and echo statements, violating the English-only rule.

**Change:**
- Line 5: `# Instalación de skills...` → `# Skill installation...`
- Line 45: `echo "=== Instalación completada ==="` → `echo "=== Installation complete ==="`
- Line 46: `echo "Ejecuta 'npx skills list'..."` → `echo "Run 'npx skills list'..."`

---

### Step 7: Remove `backend/.coverage` from git tracking

**Context:** Binary `.coverage` (52KB, changes on every test run) was tracked before .gitignore could exclude it.

**Change:**
```bash
git rm --cached backend/.coverage
```
(Already staged. Verify with `git ls-files backend/.coverage` — should be empty.)

---

### Step 8: WebSocket `_check_origin` fix

**Context:** `backend/apps/ws/consumers.py:67-72` compares `origin` against raw `FRONTEND_URL` string. When `FRONTEND_URL` has multiple origins (e.g. `localhost,staging.example.com`), string equality fails.

**Change:** Replace the `_check_origin` method to use `CORS_ALLOWED_ORIGINS` (which uses `env.list()`):
```python
def _check_origin(self, origin: str | None) -> bool:
    if not origin:
        return True
    allowed_origins = getattr(settings, "CORS_ALLOWED_ORIGINS", [])
    return origin in allowed_origins
```

Verify: existing WS tests still pass.

---

### Step 9: ADR-001 status fix

**Context:** `docs/adrs/ADR-001-rest-vs-graphql.md` has `## Status Accepted (superseded by ADR-005)` — contradictory.

**Change:** Replace with:
```markdown
## Status
Superseded by ADR-005
```

---

### Step 10: Appendix C test command fix

**Context:** AGENTS.md Appendix C shows `cd backend && pnpm test`. Backend uses `uv run pytest`, not pnpm.

**Change:**
```diff
- cd backend && pnpm test
+ cd backend && uv run pytest
```

---

### Step 11: nginx.conf CSP comment

**Context:** `frontend/nginx.conf:27` has `connect-src 'self' ws:` which allows WS to any origin. For now, add a comment noting this should be tightened in production.

**Change:** Add comment above the CSP header:
```
# DEV-ONLY CSP: ws: allows WebSocket to any origin.
# For production, restrict to wss://YOUR_DOMAIN or remove ws: entirely.
```

---

### Step 12: `.env.example` — remove staging URL

**Context:** `FRONTEND_URL=http://localhost:5173,http://staging.example.com` — `staging.example.com` looks like a real reference.

**Change:**
```diff
- FRONTEND_URL=http://localhost:5173,http://staging.example.com
+ FRONTEND_URL=http://localhost:5173
```

---

### Step 13: `.gitignore` — add missing patterns

**Context:** Missing `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `*.pyo`, `package-lock.json`.

**Change:** Add after the existing cache entries:
```
.mypy_cache/
.pytest_cache/
.ruff_cache/
*.pyo
package-lock.json
```
(Note: `package-lock.json` is added because the project uses pnpm — npm's lockfile would conflict.)

---

### Step 14: `biome.json` — enable `noNonNullAssertion`

**Context:** Rule is set to `"off"`, allowing TypeScript `!` operator (bypasses strict null checking).

**Change:**
```diff
- "noNonNullAssertion": "off"
+ "noNonNullAssertion": "error"
```
Verify: `biome check frontend/src` passes. If it fails, must fix any `!` usages first (refactor to optional chaining or type guards).

---

### Step 15: Remove stale `package-lock.json`

**Context:** `frontend/package-lock.json` (880 lines) conflicts with `pnpm-lock.yaml`. The project declared pnpm as the package manager.

**Change:**
```bash
git rm frontend/package-lock.json
```
Or delete the file and ensure `.gitignore` catches it going forward.

---

### Step 16: Restrict PostgreSQL port to localhost

**Context:** `compose.yml` exposes `5432:5432` to all network interfaces. Default credentials create a risk on untrusted networks.

**Change:**
```yaml
ports:
  - "127.0.0.1:5432:5432"
```
Verify: `docker compose config` parses without errors.

---

### Step 17: Final verification

After all changes:
1. `ls -la .github/copilot-instructions.md` — verify symlink
2. `git ls-files backend/.coverage` — should be empty
3. `git ls-files frontend/package-lock.json` — should be empty
4. `docker compose config` — parses cleanly
5. `biome check frontend/src` — passes
6. `ruff check backend/` — 0 errors
7. `mypy backend/` — 0 errors
8. `pytest` — all pass
9. `vitest run` — all pass

---

## Rollback Plan

If any verification step fails:
1. Fix the specific file that caused the failure (most issues are single-line changes)
2. Re-run the relevant check
3. If `noNonNullAssertion: "error"` breaks `biome check`, keep it as `"off"` instead and add a comment explaining why
4. If `_check_origin` change breaks WS tests, verify the test mocks and adjust

## File Change Summary

| # | File | Change Type | Risk |
|---|---|---|---|
| 1 | `.github/copilot-instructions.md` | symlink recreate | low |
| 2 | `agentic/AGENTS.md` | edit (2 spots) | low |
| 3 | `agentic/knowledge/decisions/003-drizzle-orm.md` | edit (add header) | low |
| 4 | `docs/architecture.md` | create | low |
| 5 | `agentic/AGENTS.md` | edit (template) | low |
| 6 | `install-skills.sh`, `agentic/install-skills.sh` | edit (3 lines) | low |
| 7 | `backend/.coverage` | git rm --cached | none |
| 8 | `backend/apps/ws/consumers.py` | edit (3 lines) | medium — WS logic |
| 9 | `docs/adrs/ADR-001-rest-vs-graphql.md` | edit (status line) | low |
| 10 | `agentic/AGENTS.md` | edit (1 line) | low |
| 11 | `frontend/nginx.conf` | edit (comment) | low |
| 12 | `.env.example` | edit (1 line) | low |
| 13 | `.gitignore` | edit (add 4 lines) | low |
| 14 | `biome.json` | edit (1 value) | medium — may break lint |
| 15 | `frontend/package-lock.json` | delete | low |
| 16 | `compose.yml` | edit (1 line) | low |
