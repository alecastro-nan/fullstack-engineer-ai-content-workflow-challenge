# Convention: Django App Structure

Every Django app must contain:
- `models.py` — database models with type-annotated fields
- `schema.py` — Strawberry GraphQL types, queries, and mutations
- `mutations.py` — GraphQL mutation classes (if complex)
- `queries.py` — GraphQL query classes (if complex)
- `apps.py` — Django app configuration
- `admin.py` — Django admin registration
- `tests/` — pytest test files

## Naming Rules
- Model methods: `create()`, `get_by_id()`, `update()`, `delete()`, `list_all()`
- GraphQL queries use `resolve_*` naming convention
- Mutations use `Mutation` suffix
- Always use type hints on all function signatures

## File Organization
```
campaigns/
├── __init__.py
├── models.py              # Campaign model with typed fields
├── schema.py              # Strawberry types, queries, mutations
├── mutations.py           # GraphQL mutation classes
├── queries.py             # GraphQL query classes
├── admin.py               # Django admin registration
├── apps.py                # Django app configuration
└── tests/
    ├── __init__.py
    ├── test_models.py
    └── test_graphql.py
```
