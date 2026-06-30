# Handoff — F-025: Security Hardening

## Meta
- **From:** Builder
- **To:** Code Reviewer
- **Date:** 2025-06-26 10:22 UTC

## What was done
- **GraphQL limits**: `QueryDepthLimiter(max_depth=8)`, `MaxTokensLimiter(1000)`, `MaxAliasesLimiter(5)` — all Strawberry built-in extensions, validated with real queries
- **Introspection guard**: `DisableIntrospection` when `settings.DEBUG=False`, enabled in dev
- **ALLOWED_HOSTS**: Changed from `["*"]` to `["localhost", "127.0.0.1", "0.0.0.0"]` in `base.py`; removed `["*"]` override from `development.py`
- **Prompt injection delimiters**: `---BEGIN USER BRIEF---`/`---END USER BRIEF---` wrapping + instruction reinforcement in both `draft.md` and `translation.md` prompts
- **Input length caps**: Brief validated at 5000 chars in `apps/ai/schema.py`; description/body were already capped in `apps/content/services.py`
- **CSP header**: Added to `frontend/nginx.conf` — `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' ws:; font-src 'self'`
- **ADR-008**: `docs/adrs/ADR-008-security-controls.md` documenting all decisions and rationale

## Documentation updated
- `docs/adrs/ADR-008-security-controls.md` (new)
- `agentic/tasks/session-progress.md` (status update)
- `agentic/tasks/feature_list.json` (status update)
- `agentic/runs/F-025-security-hardening/plan.md` (created during planning)

## Not done / known issues
- CSP validation requires running nginx (Docker) and hitting `curl -I` — not covered by unit tests
- `unsafe-inline` in style-src is required by Tailwind CSS — unavoidable

## Next actions
1. Code Reviewer: review all changed files (8 modified, 4 new)
2. Security Reviewer: audit API key handling, prompt injection protection, CSP config

## Quality gates (all passing)
| Gate | Result |
|---|---|
| ruff | 0 errors |
| mypy (81 files) | 0 errors |
| pytest (backend) | 144/144 |
| pnpm typecheck | 0 errors |
| pnpm test (frontend) | 88/88 |
| pnpm build | builds in ~500ms |

## Artifacts
- Plan: `agentic/runs/F-025-security-hardening/plan.md`
- ADR: `docs/adrs/ADR-008-security-controls.md`
- Tests: `backend/config/tests/test_security.py` (7 tests)
- Tests: `backend/apps/ai/tests/test_prompts.py` (7 tests)

## Files changed
```
M backend/config/schema.py              # GraphQL extensions + introspection
M backend/config/settings/base.py       # ALLOWED_HOSTS hardened
M backend/config/settings/development.py # ALLOWED_HOSTS override removed
M backend/apps/ai/prompts.py            # Prompt injection delimiters
M backend/apps/ai/schema.py             # Brief length cap
M frontend/nginx.conf                   # CSP header
A backend/config/tests/test_security.py # Security tests
A backend/apps/ai/tests/test_prompts.py # Prompt tests
A docs/adrs/ADR-008-security-controls.md # ADR
A agentic/runs/F-025-security-hardening/ # Run directory
A agentic/tasks/feature_list.json       # Status update
A agentic/tasks/session-progress.md     # Status update
```
