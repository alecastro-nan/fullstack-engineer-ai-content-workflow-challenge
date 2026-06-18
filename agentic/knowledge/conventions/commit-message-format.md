# Convention: Commit Message Format

Use Conventional Commits: `type(scope): description`

## Types
- `feat`: A new feature
- `fix`: A bug fix
- `test`: Adding or modifying tests
- `docs`: Documentation only changes
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `style`: Formatting, linting, white-space (no production code change)
- `chore`: Build process, CI, dependencies
- `infra`: Docker, deployment, infrastructure

## Examples
```
feat(api): add campaign CRUD endpoints
test(api): add campaign service unit tests
docs(adr): document REST vs GraphQL decision
fix(ai): handle rate limit error from OpenAI
chore(deps): upgrade @nestjs/core to v10
infra(docker): add healthcheck to PostgreSQL service
```

## Rules
- Limit to 72 characters for the subject line
- Use imperative mood ("add" not "added" or "adds")
- Do not end with a period
- Body (optional): wrap at 72 chars, explain what and why, not how
