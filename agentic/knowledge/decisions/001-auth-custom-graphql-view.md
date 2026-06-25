# Decision: 2025-06-25 — Custom GraphQLView instead of SchemaExtension for auth

## Context
We needed to inject an authenticated user into the Strawberry GraphQL context on every request. The initial approach used a SchemaExtension with `on_request_start`, which doesn't exist in Strawberry v0.317.x.

## Decision
Override `GraphQLView.get_context()` with a custom `AuthGraphQLView` that decodes the JWT from the `Authorization` header and sets `context.user` before resolvers run.

## Rationale
- `SchemaExtension` in v0.317.x has `on_operation`, `on_execute`, `on_parse`, `on_validate`, `resolve`, `get_results` — no `on_request_start`
- Extensions don't have direct access to the raw Django `HttpRequest`
- Custom view is the standard Strawberry Django pattern for per-request context injection
- Requires only changing one line in `urls.py`

## Alternatives
- **SchemaExtension with `on_operation`**: Could work but requires accessing the request via `info.context.request` inside each resolver — doesn't proactively set user before resolver execution
- **Django middleware**: Doesn't integrate with Strawberry context; would need `AuthenticationMiddleware` + session-based auth

## Consequences
- User is available as `info.context.user` in all resolvers
- No changes needed to individual resolvers (they already use `get_user_or_error(info)`)
- Token decode failure results in `user=None` (not an error) — `get_user_or_error` raises only if `AUTH_REQUIRED=True`
