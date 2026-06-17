# Skill: PR Submission

## Purpose
Learn how to create the final Pull Request with the correct template, verify the checklist, and push for review.

## When to Use
- When creating the final submission PR (F-024)
- When creating intermediate PRs for feedback

## Steps

### 1. Verify Branch
- Working branch must NOT be main/master
- Branch name format: `feat/<feature-name>` or `fix/<bug-description>`

### 2. Run Quality Gates
- `pnpm biome check --write .` — no lint or format errors
- `cd backend && pnpm typecheck` — no TypeScript errors
- `cd backend && pnpm test` — all tests pass
- `cd frontend && pnpm typecheck` — no TypeScript errors
- `cd frontend && pnpm test` — all tests pass

### 3. Check .env.example
- Must exist at root
- Contains all required variables without real secrets
- Matches what `compose.yml` and app code expect

### 4. Create Commit
```bash
git add .
git commit -m "feat(project): complete ACME content workflow implementation"
```

### 5. Push and Create PR
```bash
git push origin <branch>

gh pr create \
  --title "feat: ACME AI Content Workflow Platform" \
  --body-file .github/PULL_REQUEST_TEMPLATE.md \
  --draft  # Use --draft for initial submission
```

### 6. Fill PR Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code in hard-to-understand areas
- [ ] I have updated documentation
- [ ] My changes generate no new warnings
- [ ] Tests exist and pass

## Verification
- PR URL is accessible
- PR description contains all required sections
- CI pipeline (if configured) runs and passes
- No secrets in the commit history
