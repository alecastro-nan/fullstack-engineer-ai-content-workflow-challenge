# Decision: 2026-06-18 — Remove Critical Skills After SkillSpector Audit

## Context

All skills in `.agents/skills/` were audited with NVIDIA SkillSpector v2.2.3 (static analysis, no LLM). Seven skills received **DO_NOT_INSTALL** recommendations due to:

- **High/Critical severity issues**: credential references (`.env`, `.npmrc`, `access tokens`), `subprocess` with `shell=True`, `rm -rf` patterns, exfiltration vectors to external URLs, system prompt leakage
- **Supply chain risks**: unpinned dependencies
- **Tool parameter abuse**: dangerous shell commands without validation

## Skills Removed

| Skill | Score | Issues | Reason |
|-------|-------|--------|--------|
| `nestjs-best-practices` | 100 | 16 | `.env` credential refs, prompt extraction, external URLs |
| `playwright-best-practices` | 100 | 13 | Exfiltration to `api.mailinator.com`, root execution, `.env` leaks |
| `pnpm` | 100 | 8 | `.npmrc` credential refs, `rm -rf` patterns |
| `prisma-postgres` | 100 | 10 | External URLs to `api.prisma.io`, `.env`, access tokens |
| `typescript-expert` | 100 | 5 | `subprocess.run(shell=True)`, `rm -rf node_modules/` |
| `webapp-testing` | 100 | 9 | `subprocess.Popen(shell=True)`, executable scripts |
| `biome` | 75 | 3 | Prompt extraction, `rm -rf` patterns |

## Additional Cleanup

- `harness/skills/` directory removed (project-specific skill files that duplicated agent skill patterns)

## Remediation

- `install-skills.sh` updated to skip removed skills
- `skills-lock.json` pruned to 17 remaining skills
- `AGENTS.md` section 4.4 updated — references `knowledge/decisions/002-remove-critical-skills.md` for audit history

## Remaining Skills (Safe to Use)

docker-expert, javascript-typescript-jest, jest-react-testing, multi-stage-dockerfile, nestjs-expert, nestjs-patterns, playwright-generate-test, postgresql-optimization, postgresql-table-design, prisma-client-api, prisma-database-setup, react:components, sentry-sdk-setup, typescript-advanced-types, vercel-react-best-practices, vite, vitest, websocket-engineer
