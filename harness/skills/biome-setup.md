# Skill: Biome Setup & Configuration

## Purpose
Learn how to configure and use Biome for linting and formatting across the monorepo.

## When to Use
- When setting up the initial project scaffold (F-000)
- When running lint/format checks
- When adding Biome to CI pipeline

## Steps

### 1. Install Biome
```bash
pnpm add -D --save-exact @biomejs/biome
pnpm biome init  # generates biome.json
```

### 2. Configure biome.json
- Use the existing `biome.json` at root as the single source of truth
- Do NOT create per-package biome.json configs (root config applies to all)
- Ignore patterns: `dist`, `node_modules`, `.next`, `build`, `.venv`

### 3. Running Biome
```bash
# Check all files
pnpm biome check .

# Apply fixes
pnpm biome check --write .

# Format only
pnpm biome format --write .

# Lint only
pnpm biome lint .
```

### 4. Package.json Scripts
```json
{
  "scripts": {
    "lint": "biome check .",
    "lint:fix": "biome check --write .",
    "format": "biome format --write ."
  }
}
```

### 5. CI Integration
- Run `pnpm biome check .` in CI pipeline
- Fail the pipeline if any issues are found
- Use `--reporter=github` for GitHub Actions annotations

## Verification
- `pnpm biome check .` exits with code 0
- All staged files are formatted correctly
- No ESLint or Prettier config files exist (Biome replaces them)
