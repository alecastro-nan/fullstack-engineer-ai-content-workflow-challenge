# ADR-006: Agentic Directory Structure

## Status
Accepted

## Context
The project's agentic workflow artifacts (skills, knowledge, personas, task tracking, evaluation, ADRs) were scattered across the root directory with no common parent. The layout included:

- `.agents/skills/` — hidden directory for community skills
- `harness/` — personas and workflow run artifacts
- `knowledge/` — conventions, decisions, learnings
- `evaluation/` — rubric and eval cases
- `feature_list.json`, `session-progress.md` — loose root files
- `install-skills.sh`, `skills-lock.json` — loose root files
- `AGENTS.md` — source of truth at root (with `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md` as symlinks)

This scattering made it hard for agents (and humans) to understand the scope of the agentic ecosystem. Adding new agentic artifacts had no clear home.

## Decision
Consolidate all agentic workflow artifacts under a single `/agentic/` directory, with symlinks at the project root for tool compatibility. ADRs remain in `docs/adrs/` because they serve dual purpose: agentic decisions and human-readable documentation.

### New structure
```
/agentic/
├── AGENTS.md          — Source of truth (canonical)
├── skills/            — Community skills (was .agents/skills/)
├── tasks/
│   ├── feature_list.json
│   └── session-progress.md
├── knowledge/
│   ├── conventions/
│   ├── decisions/
│   └── learnings/
├── personas/          — Agent role definitions
├── runs/              — Per-task execution artifacts
├── evaluation/        — Rubric + eval cases
├── install-skills.sh
├── skills-lock.json
└── run-task.sh
```

### Root symlinks (backward compatibility)
```
AGENTS.md → agentic/AGENTS.md
CLAUDE.md → AGENTS.md
.cursorrules → AGENTS.md
.github/copilot-instructions.md → ../../agentic/AGENTS.md
feature_list.json → agentic/tasks/feature_list.json
session-progress.md → agentic/tasks/session-progress.md
install-skills.sh → agentic/install-skills.sh
skills-lock.json → agentic/skills-lock.json
```

## Consequences

### Positive
- All agentic artifacts under a single, visible directory
- `ls /agentic/` shows the complete ecosystem at a glance
- Root clutter reduced from ~12 agentic entries to 8 symlinks (which are ignored by `ls` by default)
- Clear home for new agentic artifacts (e.g., `agentic/playbooks/`, `agentic/templates/`)
- Symlinks ensure Claude Code (`CLAUDE.md`), Cursor (`.cursorrules`), and GitHub Copilot (`.github/copilot-instructions.md`) all resolve correctly
- `git mv` preserves file history for all moved files
- ADRs remain in `docs/adrs/` alongside architecture and workflow docs

### Negative
- Symlinks can confuse some editors and file explorers
- Relative paths in AGENTS.md needed updating (canonical file moved one level deeper)
- `.agents/` hidden directory replaced with visible `agentic/` (breaks `.agents/` path conventions, though symlinks help)

## Alternatives Considered
- **`.agentic/` hidden directory**: Less visible; hidden dirs are harder to discover for new contributors.
- **Keep flat, improve internally**: Doesn't solve the root clutter problem.
- **`/ops/` + `/docs/` split**: Two directories instead of one; `knowledge/` is ambiguous (operational or documentation?).
- **Everything under `/docs/`**: ADRs fit but skills, tasks, and runs are not documentation.

## References
- AGENTS.md §5 (Monorepo Folder Structure)
- AGENTS.md §11 (Knowledge Management)
