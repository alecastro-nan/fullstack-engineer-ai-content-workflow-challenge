# Decision: 2026-06-18 - Agentic directory consolidation

## Context
Agentic workflow artifacts (skills, knowledge, personas, task tracking, evaluation, symlinks) were scattered across root: `.agents/`, `harness/`, `knowledge/`, `evaluation/`, and loose root files `feature_list.json`, `session-progress.md`, `install-skills.sh`, `skills-lock.json`.

## Decision
Consolidate everything under `agentic/` with symlinks at root for backward compatibility. ADRs stay in `docs/adrs/`.

## Rationale
- Single visible directory for all agentic artifacts
- Root clutter reduced
- Symlinks maintain compatibility with Claude Code, Cursor, and Copilot
- `git mv` preserves history
