# Convention: Branch Naming

All branches must follow: `type/task-id-short-description`

## Types

| Type | When to use | Examples |
|---|---|---|
| `feat` | New feature task | `feat/F-008-review-state-machine` |
| `fix` | Bug fix or review fix | `fix/F-008-invalid-transition-guard` |
| `docs` | Documentation-only | `docs/F-024-adr-real-time` |
| `infra` | Infrastructure/Docker | `infra/F-020-ci-pipeline` |
| `refactor` | Code restructure | `refactor/F-009-ai-provider-cleanup` |
| `chore` | Build/config/tooling | `chore/F-000-eslint-setup` |

## Rules

1. **Include the task ID** — every branch must contain the `F-XXX` identifier for traceability back to the feature list
2. **Keep descriptions short** — kebab-case, max 5 words after the task ID
3. **No task ID for ephemeral branches** — planning, research, or ad-hoc branches may omit the task ID (e.g., `feat/replan-task-ordering`)
4. **One task per branch** — never bundle multiple F-XXX tasks in one branch
5. **Always branch from `feat/agentic-plan`** (the integration branch), never from other feature branches
6. **Delete after merge** — remote branches are cleaned up once the PR is merged

## Examples

```bash
# Feature task
git checkout -b feat/F-008-review-state-machine-mutations

# Fix on an in-review task
git checkout -b fix/F-006-nginx-nonroot-permissions

# Docker/infra task
git checkout -b infra/F-007-finalize-docker-compose

# Docs task
git checkout -b docs/F-024-adr-real-time

# Ephemeral (no task ID)
git checkout -b feat/replan-task-ordering
```

## Rationale

- Task ID enables instant lookup in `agentic/tasks/feature_list.json`
- Consistent prefixing groups branches by intent in `git branch --list`
- Short descriptions prevent unwieldy branch names while remaining descriptive
